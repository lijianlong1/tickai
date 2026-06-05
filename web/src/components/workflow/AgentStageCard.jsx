import React from 'react';

/**
 * 智能体阶段卡片
 *
 * 显示单个智能体的状态、进度、当前操作
 * 支持重做按钮
 */
function AgentStageCard({ agent, state, onRegenerate, isCurrent = false }) {
  const {
    name,
    display_name,
    icon = '🤖',
    color = '#6366F1',
    description = '',
  } = agent;

  const status = state?.status || 'pending';
  const progress = state?.progress || 0;
  const message = state?.message || '等待中';
  const error = state?.error;

  // 状态映射
  const statusConfig = {
    pending: {
      label: '等待中',
      bgClass: 'bg-gray-100',
      textClass: 'text-gray-600',
      icon: '⏳',
    },
    running: {
      label: '执行中',
      bgClass: 'bg-blue-100',
      textClass: 'text-blue-700',
      icon: '⚙️',
    },
    success: {
      label: '已完成',
      bgClass: 'bg-green-100',
      textClass: 'text-green-700',
      icon: '✅',
    },
    failed: {
      label: '失败',
      bgClass: 'bg-red-100',
      textClass: 'text-red-700',
      icon: '❌',
    },
  };

  const config = statusConfig[status] || statusConfig.pending;

  return (
    <div
      className={`
        relative bg-white/80 backdrop-blur-sm rounded-2xl p-5
        border-2 transition-all duration-300
        ${isCurrent ? 'shadow-lg scale-[1.02]' : 'shadow-sm hover:shadow-md'}
        ${status === 'running' ? 'border-blue-400' : 'border-gray-200'}
        ${status === 'success' ? 'border-green-300' : ''}
        ${status === 'failed' ? 'border-red-400' : ''}
      `}
    >
      {/* 当前阶段指示器 */}
      {isCurrent && (
        <div className="absolute -top-2 -right-2 w-5 h-5 bg-blue-500 rounded-full animate-ping" />
      )}

      <div className="flex items-start gap-4">
        {/* 智能体头像 */}
        <div
          className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0 shadow-md"
          style={{ background: `linear-gradient(135deg, ${color}, ${color}dd)` }}
        >
          {icon}
        </div>

        {/* 内容区 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-bold text-gray-900">
              {display_name || name}
            </h3>
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bgClass} ${config.textClass}`}>
              <span>{config.icon}</span>
              {config.label}
            </span>
          </div>

          {description && (
            <p className="text-xs text-gray-500 mb-2">{description}</p>
          )}

          {/* 进度条 */}
          {status === 'running' && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>{message}</span>
                <span>{progress}%</span>
              </div>
              <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full transition-all duration-500 rounded-full"
                  style={{
                    width: `${progress}%`,
                    background: `linear-gradient(90deg, ${color}, ${color}aa)`,
                  }}
                />
              </div>
            </div>
          )}

          {/* 错误信息 */}
          {status === 'failed' && error && (
            <div className="mt-2 p-2 rounded-lg bg-red-50 border border-red-200 text-xs text-red-600">
              {error}
            </div>
          )}

          {/* 成功信息 */}
          {status === 'success' && message && (
            <p className="text-xs text-gray-600 mt-1">✓ {message}</p>
          )}
        </div>

        {/* 重做按钮 */}
        {onRegenerate && status !== 'running' && status !== 'pending' && (
          <button
            onClick={() => onRegenerate(name)}
            className="flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
            title="重做此阶段"
          >
            <span className="mr-1">🔄</span>
            重做
          </button>
        )}
      </div>
    </div>
  );
}

export default AgentStageCard;
