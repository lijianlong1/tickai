import React, { useState, useEffect } from 'react';
import { modelConfigApi } from '../services/api';

/**
 * 模型选择器
 * 列出用户的某种类型配置，提供选择界面
 */
function ModelSelector({ type, value, onChange, label }) {
  // type: 'text' | 'image' | 'voice'
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 厂商显示名称
  const PROVIDER_LABELS = {
    openai: 'OpenAI',
    qwen: '通义千问',
    zhipu: '智谱',
    volcengine: '火山引擎',
    doubao: '豆包',
    web_speech: '浏览器内置',
  };

  // 类型显示名称
  const TYPE_LABELS = {
    text: '文本',
    image: '图像',
    voice: '语音',
  };

  useEffect(() => {
    loadConfigs();
  }, [type]);

  const loadConfigs = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await modelConfigApi.list(type);
      setConfigs(response.data?.items || []);
    } catch (err) {
      setError(err.message || '加载模型配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 当前选中的配置
  const selectedConfig = configs.find(c => c.id === value);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-semibold text-gray-700">
        {label || `${TYPE_LABELS[type] || type}模型`}
      </label>

      {loading ? (
        <div className="text-sm text-gray-500 py-2">加载中...</div>
      ) : error ? (
        <div className="text-sm text-red-500 py-2">{error}</div>
      ) : configs.length === 0 ? (
        <div className="space-y-2">
          <select
            disabled
            className="w-full px-3 py-2 rounded-lg border-2 border-gray-200 bg-gray-50 text-sm text-gray-500"
          >
            <option>暂未配置，请先添加</option>
          </select>
          <p className="text-xs text-amber-600">
            ⚠️ 请先在设置中添加 {TYPE_LABELS[type]} 模型
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          <select
            value={value || ''}
            onChange={(e) => onChange(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-3 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-500 outline-none text-sm"
          >
            <option value="">使用系统默认</option>
            {configs.map((config) => (
              <option key={config.id} value={config.id}>
                {PROVIDER_LABELS[config.provider] || config.provider} · {config.model_name}
                {config.is_default ? ' ★' : ''}
              </option>
            ))}
          </select>

          {/* 选中配置的提示 */}
          {selectedConfig && (
            <p className="text-xs text-gray-500">
              {PROVIDER_LABELS[selectedConfig.provider] || selectedConfig.provider} ·{' '}
              {selectedConfig.model_name}
              {!selectedConfig.has_api_key && type !== 'voice' && (
                <span className="text-red-500"> · 缺少 API Key</span>
              )}
            </p>
          )}

          {/* 提示 */}
          <p className="text-xs text-gray-400">
            💡 在设置 → 模型配置中管理你的模型
          </p>
        </div>
      )}
    </div>
  );
}

export default ModelSelector;
