#!/bin/bash

# 🚀 AgnFlow 流式聊天服务启动脚本
# 支持单机和多副本模式

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Redis连接
check_redis() {
    print_info "检查Redis连接..."
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            print_success "Redis连接正常"
            return 0
        else
            print_error "Redis连接失败"
            return 1
        fi
    else
        print_warning "redis-cli未安装，跳过连接检查"
        return 0
    fi
}

# 启动Redis（如果未运行）
start_redis() {
    print_info "启动Redis服务..."
    if ! check_redis; then
        if command -v docker &> /dev/null; then
            print_info "使用Docker启动Redis..."
            docker run -d --name agnflow_redis -p 6379:6379 redis:7-alpine
            sleep 3
            print_success "Redis已启动"
        else
            print_error "请手动启动Redis服务"
            exit 1
        fi
    fi
}

# 启动单机模式
start_single() {
    print_info "启动单机模式..."
    python server.py
}

# 启动多副本模式
start_cluster() {
    print_info "启动多副本模式..."
    
    if command -v docker-compose &> /dev/null; then
        print_info "使用Docker Compose启动集群..."
        docker-compose up -d
        print_success "集群已启动"
        print_info "访问地址: http://localhost"
        print_info "实例1: http://localhost:8001"
        print_info "实例2: http://localhost:8002"
        print_info "实例3: http://localhost:8003"
    else
        print_error "docker-compose未安装，无法启动集群模式"
        exit 1
    fi
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down
        print_success "服务已停止"
    else
        print_warning "docker-compose未安装，请手动停止服务"
    fi
}

# 查看日志
show_logs() {
    print_info "查看服务日志..."
    if command -v docker-compose &> /dev/null; then
        docker-compose logs -f
    else
        print_warning "docker-compose未安装，无法查看日志"
    fi
}

# 运行测试
run_tests() {
    print_info "运行Redis Pub/Sub测试..."
    python test_redis_pubsub.py
}

# 显示帮助信息
show_help() {
    echo "🚀 AgnFlow 流式聊天服务启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  single    启动单机模式"
    echo "  cluster   启动多副本模式"
    echo "  stop      停止所有服务"
    echo "  logs      查看服务日志"
    echo "  test      运行Redis测试"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 single    # 启动单机模式"
    echo "  $0 cluster   # 启动多副本模式"
    echo "  $0 test      # 运行测试"
}

# 主函数
main() {
    case "${1:-help}" in
        "single")
            start_redis
            start_single
            ;;
        "cluster")
            start_redis
            start_cluster
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            show_logs
            ;;
        "test")
            start_redis
            run_tests
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 