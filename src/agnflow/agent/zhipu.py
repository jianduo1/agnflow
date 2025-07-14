"""
API

- 语言模型: chat, assistant, agents
- 图像与视频: images, videos
- 音频: audio
- 文件与批量处理: files, batches
- 向量与嵌入: embeddings
- 知识与工具: knowledge, tools
- 检索与搜索: web_search
- 微调: fine_tunin
- 内容安全: moderations

TODO

- 语言模型✅
- 推理模型✅
- 智能体
- 视觉推理模型✅
- 搜索工具
- 音视频✅
- 视频生成模型✅
- 图像生成模型✅
- Agent模型
- 代码模型
- 向量模型
- 内容安全
- 角色扮演模型
- 智能体开发平台
- 批量处理
- 文件管理

"""

import base64
import time
import os
from dotenv import load_dotenv
from typing import Callable, Literal, Annotated as A
import logging
import subprocess
import tempfile

from zhipuai import ZhipuAI
from zhipuai.core._sse_client import StreamResponse
from zhipuai.types.chat.async_chat_completion import AsyncCompletion
from zhipuai.types.chat.chat_completion_chunk import ChatCompletionChunk
from zhipuai.types.image import ImagesResponded
from zhipuai.types.video.video_object import VideoObject

from agnflow.agent.msg import AudioMsg, ImageMsg, Msg, UserMsg, VideoMsg, inject_tool

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def zhipu_wait_for_result(model: Literal["chat", "video"], id: str, verbose: bool = False):
    """获取异步任务结果"""
    client = ZhipuAI(api_key=os.getenv("API_KEY"))
    task_status = ""
    get_cnt = 0
    result: AsyncCompletion | VideoObject = None
    while task_status != "SUCCESS" and task_status != "FAILED" and get_cnt <= 40:
        if model == "chat":
            result = client.chat.asyncCompletions.retrieve_completion_result(id=id)
        elif model == "video":
            result = client.videos.retrieve_videos_result(id=id)
            verbose = True
        task_status = result.task_status
        time.sleep(2)
        get_cnt += 1
    return result if verbose else result.choices[0].message.content


def _stream_response_generator(
    response: StreamResponse[ChatCompletionChunk],
    verbose: bool = False,
    save_file: str = None,
    model: Literal["chat", "audio"] = "chat",
):
    """流式输出生成器"""
    i = 1
    for chunk in response:
        if verbose:
            yield chunk
        elif model == "chat":
            delta = chunk.choices[0].delta
            if save_file and (save_file.endswith(".wav") or save_file.endswith(".mp3")):
                filename = save_file.format(i=i)
                if delta.audio is not None:
                    if delta.audio.data is not None:
                        with open(filename, "wb") as wav_file:
                            wav_file.write(base64.b64decode(delta.audio.data))
                            i = i + 1
            yield delta.content or ""
        elif model == "audio":
            if hasattr(chunk, "delta"):
                yield chunk.delta or ""
            else:
                yield "[END]"
                yield chunk.text or ""

    response.response.close()


# 🆓免费模型
free_model_map = {
    None: "glm-4-flash-250414",
    "vision": "glm-4v-flash",
    "vision-thinking": "glm-4.1v-thinking-flash",
    "reasoning": "glm-z1-flash",
    "image": "cogview-3-flash",
    "video": "cogvideo-x-flash",
}


# 检查并转换音频格式
def convert_to_mono(input_file: str) -> str:
    """将音频转换为单声道"""
    try:
        # 使用 ffmpeg 转换为单声道
        output_file = tempfile.mktemp(suffix=".wav")
        # ac 1 单声道
        # ar 16000 采样率16kHz
        # f wav 输出格式
        # y 覆盖输出文件
        cmd = ["ffmpeg", "-i", input_file, "-ac", "1", "-ar", "16000", "-f", "wav", "-y", output_file]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_file
    except subprocess.CalledProcessError:
        print("⚠️  ffmpeg 转换失败，尝试使用原文件...")
        return input_file
    except FileNotFoundError:
        print("⚠️  未找到 ffmpeg，请安装后重试")
        return input_file


def zhipu_chat(
    messages: str | Msg,
    model: str = None,
    tools: list[Callable] = [],
    mode: Literal["sync", "async", "stream"] = "sync",
    temperature: float = 0.7,
    top_p: float = 1.0,
    verbose: bool = False,
    save_file: str = None,
    **kwargs,
):
    """智谱AI调用接口

    参数
    - messages: 消息
    - model: 模型
    - tools: 工具
    - mode: 模式, sync: 同步, async: 异步, stream: 流式
    - temperature: 温度
    - top_p: 上文概率
    - verbose: 详细输出
    - **kwargs: 模型client其他参数

    ### 免费模型
    - glm-4-flash-250414 （model=None）
    - glm-4v-flash （model="vision"）
    - glm-4.1v-thinking （model="vision-thinking"）
    - glm-z1-flash （model="reasoning"）
    - cogview-3-flash （model="image"）
    - cogvideo-x-flash （model="video"）

    ### 语言模型:（GLM-4）
    - glm-4-flash（免费）
    - glm-4-plus
    - glm-4-air-250414
    - glm-4-airx
    - glm-4-long
    - glm-4-flashx
    - glm-4-flash-250414

    ### 视觉模型：（GLM-4V）
    - glm-4v-flash（免费）
    - glm-4v-plus-0111

    ### 推理模型：（GLM-Z1）
    - glm-z1-flash（免费）
    - glm-z1-air
    - glm-z1-airx

    ### 视觉推理模型：（GLM-4.1V）
    - glm-4.1v-thinking-flashx
    - glm-4.1v-thinking-flash

    ### 音频
    - glm-4-voice
    """
    # 参数处理
    model = free_model_map.get(model, model)
    if isinstance(messages, str):
        messages = UserMsg(messages)
    if tools:
        kwargs.update({"tools": tools, "tool_choice": "auto"})
    if mode == "stream":
        kwargs.update({"stream": True})

    # 模型调用
    client = ZhipuAI(api_key=os.getenv("API_KEY"))
    completions = client.chat.asyncCompletions if mode == "async" else client.chat.completions
    response = completions.create(model=model, messages=messages, temperature=temperature, top_p=top_p, **kwargs)

    # 结果返回
    if mode == "async":
        return lambda: zhipu_wait_for_result("chat", id=response.id, verbose=verbose)
    elif mode == "stream":
        return lambda: _stream_response_generator(response=response, verbose=verbose, save_file=save_file, model="chat")
    elif verbose:
        return response
    elif mode == "sync":
        if tools:
            return response.choices[0].message.tool_calls
        if save_file and (save_file.endswith(".wav") or save_file.endswith(".mp3")):
            audio_data = response.choices[0].message.audio.data
            with open(save_file, "wb") as wav_file:
                wav_file.write(base64.b64decode(audio_data))
        return response.choices[0].message.content
    else:
        raise ValueError(f"Invalid mode: {mode}")


def zhipu_audio(
    file: str,
    model: str = "glm-asr",
    stream: bool = False,
    verbose: bool = False,
    **kwargs,
):
    """智谱AI音频转文字

    参数
    - file: 音频文件
    - model: 模型
    - stream: 流式
    - verbose: 详细输出
    - **kwargs: 模型client其他参数
    """
    # 转换音频格式
    converted_file = convert_to_mono(file)

    client = ZhipuAI(api_key=os.getenv("API_KEY"))
    with open(converted_file, "rb") as audio_file:
        response = client.audio.transcriptions.create(model=model, file=audio_file, stream=stream, **kwargs)
        # 清理临时文件
        if converted_file != file and os.path.exists(converted_file):
            os.remove(converted_file)

        if stream:
            return lambda: _stream_response_generator(response=response, model="audio", verbose=verbose)
        else:
            return response if verbose else response.text


def zhipu_video(
    prompt: str = None,
    image_url: str = None,
    model: str = "cogvideox-flash",
    quality: Literal["quality", "speed"] = "quality",
    with_audio: bool = True,
    size: str = "1920x1080",
    fps: int = 30,
    **kwargs,
):
    """文生视频，图生视频

    参数
    - file: 视频文件
    - model: 模型
    - prompt: 文生视频提示
    - image_url: 图生视频图片url
    - quality: 输出模式，"quality"为质量优先，"speed"为速度优先
    - with_audio: 是否包含音频
    - size: 视频分辨率，支持最高4K（如: "3840x2160"）
    - fps: 帧率，可选为30或60
    - **kwargs: 模型client其他参数

    模型
    - cogvideox-2
    - cogvideox-flash（免费）

    未支持模型：vidu系列
    """
    client = ZhipuAI(api_key=os.getenv("API_KEY"))
    response: VideoObject = client.videos.generations(
        model=model, prompt=prompt, image_url=image_url, quality=quality, with_audio=with_audio, size=size, fps=fps
    )

    return lambda: zhipu_wait_for_result(model="video", id=response.id)


def zhipu_image(prompt: str = None, model: str = "cogview-3-flash", verbose: bool = False, **kwargs):
    """文生图

    参数
    - prompt: 文生图提示
    - model: 模型
    - verbose: 详细输出
    - **kwargs: 模型client其他参数

    模型：
    - cogview-4-250304
    - cogview-4
    - cogview-3-flash（免费）
    """
    client = ZhipuAI(api_key=os.getenv("API_KEY"))
    response: ImagesResponded = client.images.generations(model=model, prompt=prompt, **kwargs)

    return response if verbose else response.data[0].url


def zhipu_agent():
    """智谱AI智能体

    智能体
    - 通用翻译:
    - 专业文档翻译: doc_translation_agent
    - 社科文学翻译
    - 影视剧字幕翻译
    - 社交媒体翻译
    - AI绘图
    - AI漫画
    - 热门特效视频
    - 简历与岗位匹配助手
    - 客服话术质检 service_check_agent
    - 销售质检 sales_check_agent
    - 票据识别 bill_recognition_agent
    - 衣物识别 clothes_recognition_agent
    - 合同解析 contract_parser_agent
    - 招标解析智能体 bidding_parser_agent
    - 中标解析智能体 bidwin_parser_agent
    - 智能解题 intelligent_education_solve_agent
    - 作业批改 intelligent_education_correction_agent
    """
    pass


msg_texts = {
    "智能写作": """-上下文：我想推广公司的新产品。我的公司名为：智谱AI，新产品名为：ChatGLM大模型，是一款面向大众的AI产品。
-目标：帮我创建一条小红书平台的帖子，目的是吸引人们点击产品链接进行学习和体验。
-风格：参照Dyson等成功公司的宣传风格，它们在推广类似产品时的文案风格，同时结合小红书的文案风格。
-语调：说服性
-受众：AI产品在小红书上的主要受众是年轻人，活跃在互联网和AI领域。请针对这一群体在选择护发产品时的典型关注点来定制帖子。
-响应：保持小红书帖子简洁而深具影响力，注意要使用emoji表情，
    **平台链接以markdown格式输出显示**：［智谱AI开放平台］（https://open.bigmodel.cn/console/trialcenter）。
    **平台logo放在文案最下方**："D（https://s21.ax1x.com/2024/12/17/pALCRaT.png)*""",
    "智能翻译": """翻译以下莎士比亚戏剧《罗密欧与朱丽叶》中的选段：
\"To be, or not to be: that is the question:Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune,Or to take arms against a sea of troubles And by opposing end them.\"""",
    "实体抽取": """你现在是一个法律专家，请你对这篇判决书的内容进行分析。不要展现分析过程，直接按照下面的格式输出
## 判决书内容：
    中华人民共和国最高人民法院
        指定管辖决定书
    （2017）最高法刑辖 19 号
    关于被告单位北京盘古氏投资有限公司涉嫌骗取贷款、被告人吕涛等八人涉嫌骗取贷款、骗购外汇、非国家工作人员受贿、非法拘禁、故意毁坏会计凭证、会计账簿、财务会计报告等犯罪案件，本院经审查，依照《中华人民共和国刑事诉讼法》第二十六条的规定，决定如下：指定辽宁省大连市西岗区人民法院依照刑事第一审程序对该案进行审判。  二〇一七年三月十七日
## 定义输出格式
{
    "犯罪客体": {
        "涉及客体": ""
    },
    "犯罪主观要件-罪过形式": {
        "故意": "",
        "过失": ""
    },
    "犯罪主观要件": {
        "犯罪动机": "",
        "犯罪目的": "",
        "犯罪地点": ""
    },
    "犯罪客观要件": {
        "犯罪地点": "",
        "犯罪行为": "",
        "犯罪过程": ""
    },
    "适用法条": "",
    "判决结果时间": "",
    "判决刑期": "",
    "判决结果金额": ""
}
""",
}


@inject_tool
def query_train_info(
    departure: A[str, "出发城市或车站"], destination: A[str, "目的地城市或车站"], date: A[str, "要查询的火车日期"]
) -> str:
    """根据用户提供的信息查询火车时刻"""
    return "2024年1月1日从北京南站到上海的火车票"


msg_images = {
    "图像描述生成": ImageMsg(
        "对图像进行详细描述，包括主要元素、场景、颜色等。",
        "https://cdn.bigmodel.cn/markdown/1735118177180image.png?attname=image.png",
    ),
    "图像分类": ImageMsg(
        "仔细观察图像，给出图像中的狗品种。",
        "https://cdn.bigmodel.cn/markdown/1735118460293image.png?attname=image.png",
    ),
    "视觉推理": ImageMsg(
        "根据图中的内容，推测出当天的天气", "https://cdn.bigmodel.cn/markdown/1735118533368image.png?attname=image.png"
    ),
    "视觉问答（VQA）": ImageMsg(
        "给你分享一个我最近看演唱会的照片", "https://cdn.bigmodel.cn/markdown/1735118599591image.png?attname=image.png"
    ),
    "图像情感分析": ImageMsg(
        "分析并描述图像所传达的主要情感或情绪。",
        "https://cdn.bigmodel.cn/markdown/1735118688747image.png?attname=image.png",
    ),
    "图表问答": ImageMsg(
        "请你帮我分析一下图片中的房价走势，并预测接下来一年的趋势是什么",
        "http://cdn.bigmodel.cn/markdown/1735635250726成都二手房价今年价格图.jpeg?attname=成都二手房价今年价格图.jpeg",
    ),
    "社交媒体内容生成": ImageMsg(
        "据图片内容创作一篇吸引人的小红书（徒步旅行）文案",
        "https://cdn.bigmodel.cn/markdown/1735118803138image.png?attname=image.png",
    ),
    "教育应用": ImageMsg(
        "图中反应了什么物理学现象", "https://cdn.bigmodel.cn/markdown/1735118908375image.png?attname=image.png"
    ),
    "质量检测": ImageMsg(
        "识别图中有几个坏果", "https://cdn.bigmodel.cn/markdown/1735119051024image.png?attname=image.png"
    ),
    "商品描述生成": ImageMsg(
        "给图中的物品生成一个商品标题，用于淘宝商店!",
        "https://cdn.bigmodel.cn/markdown/1735119077344image.png?attname=image.png",
    ),
    "数据标注": ImageMsg(
        "准确识别图像中汽车的类型和颜色，并且按照 json格式输出",
        "https://cdn.bigmodel.cn/markdown/1735119156174image.png?attname=image.png",
    ),
    "保险单信息提取": ImageMsg(
        """DEFINE ROLE AS "发票识别专家":
    知识领域 = [发票识别、税务、财务会计]
    技能 = [文字识别、信息提取、格式验证、数据处理]
    经验 = "资深"
#定义发票字段结构
invoice_fields = {
  “发票基础信息”: {
        “发票类型”: {“description”: “发票种类，如增值税电子普通发票”},
        “发票代码”: {“description”: “发票左上角的10-12位数字代码”},
        “发票号码”: {“description”: “发票右上角的8位数字”},
        “开票日期”: {“description”: “格式为YYYY年MM月DD日”},
        “校验码”: {“description”: “发票右上角的校验码”},
        “机器编号”: {“description”: “发票机器编号”}
  },
  “购买方信息”: {
        “名称”: {“description”: “购买方完整名称”},
        “纳税人识别号”: {“description”: “购买方的统一社会信用代码”},
        “地址电话”: {“description”: “购买方的地址和联系电话”},
        “开户行及账号”: {“description”: “购买方的开户银行及账号”}
  },
  “销售方信息”: {
        “名称”: {“description”: “销售方完整名称”},
        “纳税人识别号”: {“description”: “销售方的统一社会信用代码”},
        “地址电话”: {“description”: “销售方的地址和联系电话”},
        “开户行及账号”: {“description”: “销售方的开户银行及账号”}
  },
  “商品信息”: {
        “货物或应税劳务服务名称”: {“description”: “商品或服务的名称”},
        “规格型号”: {“description”: “商品的规格型号”},
        “单位”: {“description”: “计量单位”},
        “数量”: {“description”: “商品数量”},
        “单价”: {“description”: “商品单价”}
  },
  “金额信息”: {
        “金额”: {“description”: “不含税金额”},
        “税率”: {“description”: “适用税率”},
        “税额”: {“description”: “税收金额”},
        “价税合计_大写”: {“description”: “含税总金额的中文大写”},
        “价税合计_小写”: {“description”: “含税总金额的数字表示”}
  },
  “开票方信息”: {
        “收款人”: {“description”: “收款人姓名”},
        “复核人”: {“description”: “复核人姓名”},
         “开票人”: {“description”: “开票人姓名”},
        “销售方盖章”: {“description”: “销售方的印章信息”}
  }
}

def extract_invoice_fields(image_content):
‘’‘’‘’
Step1: 识别发票类型
Step2: 按照各维度定位并提取字段
Step3: 进行字段验证和格式化
Step4: 返回结构化数据
‘’‘’‘’
output = {
        category: {field: “” for field in fields.keys()}
        for category, fields in invoice_fields.items()
}
return output
MAIN PROCESS(image):
user_input = 读取(‘’‘’‘’[image]‘’‘’‘’)
return extract_invoice_fields(user_input)

严格按照json格式，输出MAIN PROCESS的执行结果，禁止附加任何
的解释:""",
        "http://https://cdn.bigmodel.cn/http://markdown/1735637424313屏幕截图%202024-12-06%20143452.png?attname=屏幕截图+2024-12-06+143452.png",
    ),
    "肤质图片测试建议": ImageMsg(
        """＃ Role： 专业护肤顾问
## Description：我是一位专业的护肤顾问， 擅长通过图片分析肤质状况，
并提供个性化的护肤建议和方案规划。
## Commands
/analyze- 分析肤质状况
Idiagnose - 问题诊断
/plan- 护肤方案定制
/routine - 日常护理建议
/product - 产品类型推荐
llifestyle - 生活习惯建议
/progress - 跟踪改善进度
""",
        "https://cdn.bigmodel.cn/markdown/1735119024866image.png?attname=image.png",
    ),
}
msg_video = VideoMsg(
    "描述一下视频", "https://aigc-files.bigmodel.cn/api/cogvideo/be4922f6-5de4-11f0-afc2-be3559d9b1c6_0.mp4"
)


def pprint(*values, stream=False):
    """pretty print"""
    import json

    _values = []
    for value in values:
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value, indent=4, ensure_ascii=False)
        _values.append(value)
    if stream:
        print(*_values, end="", flush=True)
    else:
        print(*_values)


if __name__ == "__main__":
    ...
    # 🚀 问答
    # 同步调用
    response = zhipu_chat(messages=msg_texts["智能写作"], mode="sync")
    print(response)
    # 流式输出
    genertor = zhipu_chat(messages=msg_texts["实体抽取"], mode="stream")
    for chunk in genertor():
        pprint(chunk, stream=True)
    # 异步调用
    wait_for_result = zhipu_chat(messages=msg_texts["智能翻译"], mode="async")
    print(wait_for_result())

    # 🔧 工具调用
    msg = "使用工具，帮我查询从2024年1月20日，从北京出发前往上海的航班"
    tool_calls = zhipu_chat(messages=msg, tools=[query_train_info.schema])
    print(tool_calls)

    # 📷 图片描述
    response = zhipu_chat(messages=msg_images["社交媒体内容生成"], model="vision")
    print(response)

    # 🤔 推理
    msg = "一个袋子中有5个红球和3个蓝球,随机抽取2个球,抽到至少1个红球的概率为:"
    response = zhipu_chat(messages=msg, model="reasoning", mode="sync")
    print(response)  # 同步调用
    genertor = zhipu_chat(messages=msg, model="reasoning", mode="stream")
    for chunk in genertor():
        pprint(chunk, stream=True)  # 流式输出
    wait_for_result = zhipu_chat(messages=msg, model="reasoning", mode="async")
    print(wait_for_result())  # 异步调用

    # 👁 视觉推理
    response = zhipu_chat(messages=msg_images["视觉推理"], model="vision-thinking")
    print(response)

    # 🎤 音频问答
    # 同步
    msg = AudioMsg("您好", "assets/hello.mp3")
    response = zhipu_chat(messages=msg, model="glm-4-voice", save_file="assets/output2.wav")
    print(response)
    # 流式
    msg = AudioMsg(url="assets/voice/hello.mp3")
    generator = zhipu_chat(messages=msg, model="glm-4-voice", save_file="assets/output3-{i}.wav", mode="stream")
    for chunk in generator():
        pprint(chunk, stream=True)

    # 🎤 音频转文字
    # 同步
    response = zhipu_audio(file="assets/voice/hello.mp3", model="glm-asr")
    print(response)
    #  流式
    generator = zhipu_audio(file="assets/voice/hello.mp3", model="glm-asr", stream=True)
    for chunk in generator(): 
        pprint(chunk, stream=True)

    # 🎥 视频生成
    wait_for_result = zhipu_video(prompt="一个美丽的女孩在海边散步")
    print(wait_for_result())

    # 🎨 文生图
    response = zhipu_image(prompt="一只可爱的小猫咪")
    print(response)
