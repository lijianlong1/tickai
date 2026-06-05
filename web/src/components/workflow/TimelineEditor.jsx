import React, { useState, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../../services/api';

/**
 * 时间轴编辑器
 *
 * 功能：
 * - 显示视频时间轴（每个镜头一个块）
 * - 选中镜头后编辑字幕、调整时长
 * - 视频预览
 * - 重新合成
 */
function TimelineEditor({ workflowId, panels: initialPanels, videoUrl, onUpdate, onRecompose }) {
  const [panels, setPanels] = useState(initialPanels || []);
  const [selectedIdx, setSelectedIdx] = useState(1);
  const [videoTime, setVideoTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [editingField, setEditingField] = useState(null); // 'narration' | 'duration' | null
  const [saving, setSaving] = useState(false);

  const videoRef = useRef(null);

  // 计算总时长
  const totalDuration = panels.reduce((sum, p) => sum + (p.duration || 0), 0);

  // 时间格式化
  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  // 选中的镜头
  const selectedPanel = panels.find(p => p.index === selectedIdx) || panels[0];

  // 保存镜头修改
  const savePanel = async (idx, updates) => {
    setSaving(true);
    try {
      const { workflowApi } = await import('../../services/api');
      await workflowApi.updatePanel(workflowId, idx, updates);
      // 更新本地状态
      setPanels(prev => prev.map(p =>
        p.index === idx ? { ...p, ...updates } : p
      ));
      if (onUpdate) onUpdate(idx, updates);
    } catch (err) {
      alert('保存失败: ' + err.message);
    } finally {
      setSaving(false);
      setEditingField(null);
    }
  };

  // 重新合成
  const handleRecompose = async () => {
    if (onRecompose) {
      await onRecompose();
    }
  };

  return (
    <div className="space-y-4">
      {/* 视频播放器 */}
      {videoUrl && (
        <div className="bg-black rounded-2xl overflow-hidden">
          <video
            ref={videoRef}
            src={`${API_BASE_URL.replace('/api', '')}${videoUrl}`}
            controls
            className="w-full max-h-[60vh]"
            onTimeUpdate={(e) => setVideoTime(e.target.currentTime)}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />
        </div>
      )}

      {/* 时间轴 */}
      <div className="bg-white rounded-2xl shadow-lg p-5 border border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-700">时间轴</h3>
          <span className="text-xs text-gray-500">
            总时长：<span className="font-semibold text-gray-900">{formatTime(totalDuration)}</span>
          </span>
        </div>

        {/* 时间刻度 */}
        <div className="relative h-8 mb-1">
          {Array.from({ length: Math.ceil(totalDuration / 5) + 1 }, (_, i) => i * 5).map(t => (
            <div
              key={t}
              className="absolute top-0 bottom-0 border-l border-gray-300 text-xs text-gray-500 pl-1"
              style={{ left: `${(t / totalDuration) * 100}%` }}
            >
              {t}s
            </div>
          ))}
        </div>

        {/* 镜头块 */}
        <div className="flex h-16 rounded-lg overflow-hidden border-2 border-gray-200">
          {panels.map((panel) => {
            const width = `${((panel.duration || 5) / totalDuration) * 100}%`;
            const isSelected = panel.index === selectedIdx;
            return (
              <div
                key={panel.index}
                onClick={() => setSelectedIdx(panel.index)}
                className={`
                  relative cursor-pointer transition-all duration-200 border-r border-white/30
                  ${isSelected ? 'ring-2 ring-blue-500 ring-inset z-10' : 'hover:opacity-90'}
                `}
                style={{ width, background: `linear-gradient(135deg, #6366F1${isSelected ? 'FF' : 'CC'}, #8B5CF6${isSelected ? 'FF' : 'CC'})` }}
                title={`镜头 ${panel.index}: ${panel.scene?.slice(0, 20) || '无描述'}`}
              >
                <div className="absolute inset-0 flex flex-col items-center justify-center text-white p-1">
                  <span className="text-xs font-bold">#{panel.index}</span>
                  <span className="text-[10px] opacity-80">{panel.duration?.toFixed(1)}s</span>
                </div>
                {panel.subject_image_url && (
                  <div className="absolute top-0 right-0 w-2 h-2 bg-green-400 rounded-full m-0.5" />
                )}
                {panel.audio_url && (
                  <div className="absolute bottom-0 right-0 w-2 h-2 bg-yellow-400 rounded-full m-0.5" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 选中镜头的编辑器 */}
      {selectedPanel && (
        <div className="bg-white rounded-2xl shadow-lg p-5 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-gray-900">
              镜头 {selectedPanel.index}
            </h3>
            <span className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600">
              {selectedPanel.camera || '中景'}
            </span>
          </div>

          {/* 双图预览 */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1">主体图</p>
              <div className="aspect-square rounded-xl overflow-hidden bg-gray-100 border-2 border-gray-200">
                {selectedPanel.subject_image_url ? (
                  <img
                    src={`${API_BASE_URL.replace('/api', '')}${selectedPanel.subject_image_url}`}
                    alt="主体"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-3xl">
                    👤
                  </div>
                )}
              </div>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1">背景图</p>
              <div className="aspect-square rounded-xl overflow-hidden bg-gray-100 border-2 border-gray-200">
                {selectedPanel.background_image_url ? (
                  <img
                    src={`${API_BASE_URL.replace('/api', '')}${selectedPanel.background_image_url}`}
                    alt="背景"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-3xl">
                    🏞️
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 场景描述 */}
          <div className="mb-4">
            <label className="block text-xs font-semibold text-gray-700 mb-1">场景</label>
            <p className="text-sm text-gray-600 p-3 rounded-lg bg-gray-50">
              {selectedPanel.scene || '（暂无描述）'}
            </p>
          </div>

          {/* 旁白编辑 */}
          <div className="mb-4">
            <label className="block text-xs font-semibold text-gray-700 mb-1">旁白</label>
            {editingField === 'narration' ? (
              <div className="flex gap-2">
                <textarea
                  defaultValue={selectedPanel.narration || ''}
                  className="flex-1 px-3 py-2 rounded-lg border-2 border-blue-500 outline-none text-sm"
                  rows={2}
                  onBlur={(e) => savePanel(selectedPanel.index, { narration: e.target.value })}
                  autoFocus
                />
                <button
                  onClick={() => setEditingField(null)}
                  className="px-3 py-1 rounded-lg bg-gray-200 text-gray-700 text-sm"
                >
                  取消
                </button>
              </div>
            ) : (
              <div
                onClick={() => setEditingField('narration')}
                className="text-sm text-gray-800 p-3 rounded-lg bg-blue-50 border-2 border-blue-100 cursor-pointer hover:bg-blue-100"
              >
                {selectedPanel.narration || '点击编辑旁白...'}
              </div>
            )}
          </div>

          {/* 时长调整 */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-semibold text-gray-700">时长</label>
              <span className="text-xs text-gray-500">
                {selectedPanel.duration?.toFixed(1)} 秒
              </span>
            </div>
            <input
              type="range"
              min="2"
              max="15"
              step="0.5"
              value={selectedPanel.duration || 5}
              onChange={(e) => {
                const newDuration = parseFloat(e.target.value);
                setPanels(prev => prev.map(p =>
                  p.index === selectedPanel.index ? { ...p, duration: newDuration } : p
                ));
              }}
              onMouseUp={(e) => {
                const newDuration = parseFloat(e.target.value);
                savePanel(selectedPanel.index, { duration: newDuration });
              }}
              onTouchEnd={(e) => {
                const newDuration = parseFloat(e.target.value);
                savePanel(selectedPanel.index, { duration: newDuration });
              }}
              className="w-full"
            />
          </div>

          {/* 音频播放器 */}
          {selectedPanel.audio_url && (
            <div className="mb-4">
              <p className="text-xs font-semibold text-gray-700 mb-1">语音</p>
              <audio
                controls
                src={`${API_BASE_URL.replace('/api', '')}${selectedPanel.audio_url}`}
                className="w-full"
              />
            </div>
          )}
        </div>
      )}

      {/* 底部操作栏 */}
      <div className="flex gap-3">
        <button
          onClick={handleRecompose}
          disabled={saving}
          className="flex-1 px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:scale-[1.02] transition-transform disabled:opacity-50"
        >
          {saving ? '合成中...' : '🎬 重新合成视频'}
        </button>
      </div>
    </div>
  );
}

export default TimelineEditor;
