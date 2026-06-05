import React, { useEffect, useState, useRef } from 'react';
import { videoApi, API_BASE_URL } from '../services/api';

/**
 * 视频预览组件
 * - 显示当前生成状态
 * - 完成后展示视频播放器
 * - 支持下载
 */
function VideoPreview({ projectId, status: initialStatus, onComplete }) {
  const [status, setStatus] = useState(initialStatus);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [videoUrl, setVideoUrl] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [thumbnailUrl, setThumbnailUrl] = useState(null);
  const pollRef = useRef(null);

  // 状态文本映射
  const STATUS_LABELS = {
    pending: '排队中',
    generating_script: '生成剧本',
    generating_images: '生成画面',
    generating_voice: '生成语音',
    composing: '合成视频',
    completed: '已完成',
    failed: '生成失败',
  };

  // 状态颜色
  const STATUS_COLORS = {
    pending: 'bg-gray-100 text-gray-700',
    generating_script: 'bg-blue-100 text-blue-700',
    generating_images: 'bg-purple-100 text-purple-700',
    generating_voice: 'bg-pink-100 text-pink-700',
    composing: 'bg-orange-100 text-orange-700',
    completed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
  };

  useEffect(() => {
    if (!projectId) return;

    const pollStatus = async () => {
      try {
        const response = await videoApi.getStatus(projectId);
        const data = response.data;
        setStatus(data.status);
        setProgress(data.progress);
        setCurrentStep(data.current_step || '');
        setErrorMessage(data.error_message);

        if (data.video_url) {
          setVideoUrl(`${API_BASE_URL.replace('/api', '')}${data.video_url}`);
        }
        if (data.thumbnail_url) {
          setThumbnailUrl(`${API_BASE_URL.replace('/api', '')}${data.thumbnail_url}`);
        }

        // 完成或失败时停止轮询
        if (data.status === 'completed' || data.status === 'failed') {
          if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
          }
          if (data.status === 'completed' && onComplete) {
            onComplete(data);
          }
        }
      } catch (err) {
        console.error('查询状态失败:', err);
      }
    };

    // 立即查询一次
    pollStatus();

    // 启动轮询（每 2 秒）
    pollRef.current = setInterval(pollStatus, 2000);

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
      }
    };
  }, [projectId]);

  // 下载视频
  const handleDownload = async () => {
    try {
      const blob = await videoApi.download(projectId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `video_${projectId}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('下载失败：' + err.message);
    }
  };

  // 状态徽章
  const StatusBadge = () => (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[status] || 'bg-gray-100'}`}
    >
      {STATUS_LABELS[status] || status}
    </span>
  );

  // 进行中
  if (status !== 'completed' && status !== 'failed') {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <StatusBadge />
          <span className="text-sm text-gray-600">{progress}%</span>
        </div>

        {/* 进度条 */}
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* 当前步骤 */}
        {currentStep && (
          <p className="text-sm text-gray-600 flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
            {currentStep}
          </p>
        )}

        {/* 缩略图（如果有） */}
        {thumbnailUrl && (
          <div className="mt-4">
            <img
              src={thumbnailUrl}
              alt="缩略图"
              className="w-full rounded-lg shadow-md"
            />
          </div>
        )}
      </div>
    );
  }

  // 失败
  if (status === 'failed') {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <StatusBadge />
        </div>
        <div className="p-4 rounded-lg bg-red-50 border border-red-200">
          <p className="text-red-700 font-medium">生成失败</p>
          {errorMessage && (
            <p className="text-red-600 text-sm mt-1">{errorMessage}</p>
          )}
        </div>
      </div>
    );
  }

  // 完成
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <StatusBadge />
        <button
          onClick={handleDownload}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium hover:shadow-lg transition-shadow flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          下载视频
        </button>
      </div>

      {videoUrl && (
        <video
          src={videoUrl}
          controls
          className="w-full rounded-lg shadow-lg"
          poster={thumbnailUrl}
        />
      )}
    </div>
  );
}

export default VideoPreview;
