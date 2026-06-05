import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useUser } from '../contexts/UserContext';

function MusicCreatePage() {
  const { user } = useUser();
  const [formData, setFormData] = useState({
    prompt: '',
    style: 'electronic',
    duration: 30,
    tempo: 120
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    
    // TODO: 这里后续接入真实的 AI 音乐创作 API
    setTimeout(() => {
      setResult({
        title: 'AI 生成音乐',
        style: formData.style,
        duration: formData.duration,
        tempo: formData.tempo,
        audioUrl: '#' // 实际使用时会是真实的音频 URL
      });
      setIsGenerating(false);
    }, 3000);
  };

  const handlePlay = () => {
    setIsPlaying(!isPlaying);
    // TODO: 实际播放音频
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-50 relative overflow-hidden">
      <Navbar />
      
      {/* 背景装饰 */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 container mx-auto px-6 pt-24 pb-20">
        {/* 返回按钮 */}
        <Link to="/create" className="inline-flex items-center text-gray-600 hover:text-purple-600 mb-8 transition-colors">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回创作中心
        </Link>

        {/* 页面标题 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 border border-purple-200 text-purple-700 text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-2 animate-pulse"></span>
            AI 音乐创作
          </div>
          <h1 className="text-5xl font-black mb-6">
            <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent">
              AI 音乐生成
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            描述你想要的音乐风格，AI 为你创作独特的音乐作品
          </p>
        </div>

        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧表单 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="prompt" className="block text-sm font-semibold text-gray-700 mb-2">
                  音乐描述
                </label>
                <textarea
                  id="prompt"
                  rows={4}
                  value={formData.prompt}
                  onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 outline-none resize-none"
                  placeholder="描述你想要的音乐风格，例如：轻松愉快的电子音乐，适合夏日派对..."
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  音乐风格
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'electronic', label: '电子音乐', emoji: '🎹' },
                    { value: 'classical', label: '古典音乐', emoji: '🎻' },
                    { value: 'jazz', label: '爵士乐', emoji: '🎷' },
                    { value: 'rock', label: '摇滚乐', emoji: '🎸' },
                    { value: 'hiphop', label: '嘻哈', emoji: '🎤' },
                    { value: 'ambient', label: '氛围音乐', emoji: '🌙' }
                  ].map((style) => (
                    <button
                      key={style.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, style: style.value })}
                      className={`py-3 px-4 rounded-lg font-medium transition-all duration-300 flex items-center justify-center gap-2 ${
                        formData.style === style.value
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      <span>{style.emoji}</span>
                      {style.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label htmlFor="duration" className="block text-sm font-semibold text-gray-700 mb-2">
                  时长（秒）
                </label>
                <input
                  type="range"
                  id="duration"
                  min="10"
                  max="120"
                  step="5"
                  value={formData.duration}
                  onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>10秒</span>
                  <span className="font-semibold text-purple-600">{formData.duration}秒</span>
                  <span>120秒</span>
                </div>
              </div>

              <div>
                <label htmlFor="tempo" className="block text-sm font-semibold text-gray-700 mb-2">
                  节奏（BPM）
                </label>
                <input
                  type="range"
                  id="tempo"
                  min="60"
                  max="180"
                  step="10"
                  value={formData.tempo}
                  onChange={(e) => setFormData({ ...formData, tempo: parseInt(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>慢速</span>
                  <span className="font-semibold text-purple-600">{formData.tempo} BPM</span>
                  <span>快速</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={isGenerating || !user || (user.balance || 0) <= 0}
                className="w-full relative group overflow-hidden px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-700 via-pink-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <span className="relative flex items-center justify-center">
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      创作中...
                    </>
                  ) : !user ? (
                    <>
                      <span className="mr-2">🔒</span>
                      请您登录
                    </>
                  ) : (user.balance || 0) <= 0 ? (
                    <>
                      <span className="mr-2">💰</span>
                      请您登录并充值
                    </>
                  ) : (
                    <>
                      <span className="mr-2">🎵</span>
                      开始创作
                    </>
                  )}
                </span>
              </button>
            </form>
          </div>

          {/* 右侧预览 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <h3 className="text-xl font-bold mb-6 text-gray-900">音乐预览</h3>
            {result ? (
              <div className="space-y-6">
                {/* 音频播放器 */}
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={handlePlay}
                        className="w-14 h-14 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 text-white flex items-center justify-center hover:shadow-lg transition-shadow"
                      >
                        {isPlaying ? (
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                          </svg>
                        ) : (
                          <svg className="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        )}
                      </button>
                      <div>
                        <p className="text-sm text-gray-600">时长</p>
                        <p className="font-semibold text-gray-900">{result.duration}秒</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">节奏</p>
                      <p className="font-semibold text-gray-900">{result.tempo} BPM</p>
                    </div>
                  </div>

                  {/* 波形动画 */}
                  <div className="flex items-center justify-center gap-1 h-16">
                    {Array.from({ length: 40 }).map((_, i) => (
                      <div
                        key={i}
                        className={`w-1 bg-gradient-to-t from-purple-600 to-pink-600 rounded-full transition-all duration-300 ${
                          isPlaying ? 'animate-pulse' : ''
                        }`}
                        style={{
                          height: `${Math.random() * 100}%`,
                          animationDelay: `${i * 0.05}s`
                        }}
                      ></div>
                    ))}
                  </div>
                </div>

                {/* 音乐信息 */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-sm text-gray-600 mb-2">音乐风格</p>
                  <p className="text-gray-900 capitalize">{result.style}</p>
                </div>

                {/* 操作按钮 */}
                <div className="flex gap-2">
                  <button className="flex-1 px-4 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-medium hover:shadow-lg transition-shadow">
                    下载音乐
                  </button>
                  <button className="flex-1 px-4 py-3 rounded-lg border-2 border-gray-200 text-gray-700 font-medium hover:bg-gray-50 transition-colors">
                    重新生成
                  </button>
                </div>
              </div>
            ) : (
              <div className="h-96 flex flex-col items-center justify-center text-gray-400">
                <span className="text-6xl mb-4">🎵</span>
                <p>填写左侧表单后，AI 将为你创作音乐</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MusicCreatePage;