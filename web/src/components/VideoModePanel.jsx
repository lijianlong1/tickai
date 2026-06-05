import React, { useState } from 'react';
import { useUser } from '../contexts/UserContext';
import { videoApi } from '../services/api';
import ModelSelector from './ModelSelector';
import CharacterSelector from './CharacterSelector';
import SubtitleConfigPanel, { DEFAULT_SUBTITLE_CONFIG } from './SubtitleConfigPanel';
import VideoPreview from './VideoPreview';

/**
 * 视频模式主面板
 * 包含剧本输入、参数配置、模型选择、角色选择、字幕配置、生成按钮
 */
function VideoModePanel() {
  const { user } = useUser();
  const [formData, setFormData] = useState({
    title: '',
    script_prompt: '',
    ratio: '16:9',
    duration: 30,
    character_ids: [],
    text_model_id: null,
    image_model_id: null,
    voice_model_id: null,
    subtitle_config: DEFAULT_SUBTITLE_CONFIG,
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [currentProjectId, setCurrentProjectId] = useState(null);

  const RATIO_OPTIONS = [
    { value: '16:9', label: '16:9 横屏', desc: 'YouTube/B站' },
    { value: '9:16', label: '9:16 竖屏', desc: '抖音/快手' },
    { value: '1:1', label: '1:1 方形', desc: 'Instagram' },
    { value: '4:3', label: '4:3 经典', desc: '传统媒体' },
  ];

  const DURATION_OPTIONS = [
    { value: 10, label: '10 秒' },
    { value: 30, label: '30 秒' },
    { value: 60, label: '60 秒' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsGenerating(true);

    try {
      // 构造请求体
      const requestBody = {
        title: formData.title,
        script_prompt: formData.script_prompt,
        ratio: formData.ratio,
        duration: formData.duration,
        character_ids: formData.character_ids,
        model_config: {
          text: formData.text_model_id ? { config_id: formData.text_model_id } : {},
          image: formData.image_model_id ? { config_id: formData.image_model_id } : {},
          voice: formData.voice_model_id ? { config_id: formData.voice_model_id } : {},
        },
        subtitle_config: formData.subtitle_config.enabled ? formData.subtitle_config : null,
      };

      const response = await videoApi.generate(requestBody);
      setCurrentProjectId(response.data.project_id);
    } catch (err) {
      setError(err.message || '启动生成失败');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 视频预览（生成中或完成后） */}
      {currentProjectId && (
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-3xl p-6 border-2 border-blue-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">🎬</span>
            视频生成进度
          </h3>
          <VideoPreview projectId={currentProjectId} status="pending" />
        </div>
      )}

      {/* 表单 */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 错误提示 */}
        {error && (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-600">
            {error}
          </div>
        )}

        {/* 标题 + 描述 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              视频标题
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none"
              placeholder="给你的视频起个名字"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              时长
            </label>
            <div className="grid grid-cols-3 gap-2">
              {DURATION_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, duration: opt.value })}
                  className={`px-3 py-3 rounded-xl border-2 font-medium text-sm transition-all ${
                    formData.duration === opt.value
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 比例 */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            画面比例
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {RATIO_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setFormData({ ...formData, ratio: opt.value })}
                className={`p-3 rounded-xl border-2 text-left transition-all ${
                  formData.ratio === opt.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className={`font-semibold text-sm ${
                  formData.ratio === opt.value ? 'text-blue-700' : 'text-gray-900'
                }`}>
                  {opt.label}
                </div>
                <div className="text-xs text-gray-500 mt-1">{opt.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* 剧本 */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            剧本描述
          </label>
          <textarea
            rows={4}
            value={formData.script_prompt}
            onChange={(e) => setFormData({ ...formData, script_prompt: e.target.value })}
            className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none resize-none"
            placeholder="描述你想要的视频内容，例如：一个小英雄在森林里冒险，遇到了一只会说话的狐狸..."
            required
            minLength={10}
          />
        </div>

        {/* 模型选择 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-xl bg-gray-50">
          <ModelSelector
            type="text"
            value={formData.text_model_id}
            onChange={(v) => setFormData({ ...formData, text_model_id: v })}
            label="文本模型"
          />
          <ModelSelector
            type="image"
            value={formData.image_model_id}
            onChange={(v) => setFormData({ ...formData, image_model_id: v })}
            label="图像模型"
          />
          <ModelSelector
            type="voice"
            value={formData.voice_model_id}
            onChange={(v) => setFormData({ ...formData, voice_model_id: v })}
            label="语音模型"
          />
        </div>

        {/* 角色选择 */}
        <div className="p-4 rounded-xl bg-gray-50">
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            角色（可多选，用于分镜中切换）
          </label>
          <CharacterSelector
            value={formData.character_ids}
            onChange={(ids) => setFormData({ ...formData, character_ids: ids })}
            multi={true}
          />
        </div>

        {/* 字幕配置 */}
        <div className="p-4 rounded-xl bg-gray-50">
          <SubtitleConfigPanel
            value={formData.subtitle_config}
            onChange={(cfg) => setFormData({ ...formData, subtitle_config: cfg })}
          />
        </div>

        {/* 生成按钮 */}
        <button
          type="submit"
          disabled={isGenerating || !user || (user.balance || 0) <= 0 || currentProjectId}
          className="w-full relative group overflow-hidden px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-blue-700 via-purple-700 to-pink-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <span className="relative flex items-center justify-center">
            {isGenerating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                启动中...
              </>
            ) : !user ? (
              <>🔒 请先登录</>
            ) : (user.balance || 0) <= 0 ? (
              <>💰 余额不足，请先充值</>
            ) : currentProjectId ? (
              <>⏳ 任务进行中...</>
            ) : (
              <>🎬 开始生成视频</>
            )}
          </span>
        </button>
      </form>
    </div>
  );
}

export default VideoModePanel;
