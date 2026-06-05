import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useUser } from '../contexts/UserContext';

function ComicCreatePage() {
  const { user } = useUser();
  const [formData, setFormData] = useState({
    title: '',
    style: 'anime',
    description: '',
    panels: 4
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    
    // TODO: 这里后续接入真实的 AI 漫剧制作 API
    setTimeout(() => {
      setResult({
        image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=beautiful%20anime%20manga%20comic%20strip%20with%20multiple%20panels%20storytelling%20colorful%20detailed&image_size=landscape_16_9',
        title: formData.title,
        panels: formData.panels
      });
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 relative overflow-hidden">
      <Navbar />
      
      {/* 背景装饰 */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-cyan-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-teal-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 container mx-auto px-6 pt-24 pb-20">
        {/* 返回按钮 */}
        <Link to="/create" className="inline-flex items-center text-gray-600 hover:text-blue-600 mb-8 transition-colors">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回创作中心
        </Link>

        {/* 页面标题 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-cyan-100 border border-blue-200 text-blue-700 text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
            AI 漫剧制作
          </div>
          <h1 className="text-5xl font-black mb-6">
            <span className="bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent">
              创作你的漫画故事
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            输入故事描述，AI 自动生成精美的漫画作品
          </p>
        </div>

        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧表单 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2">
                  漫画标题
                </label>
                <input
                  type="text"
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 outline-none"
                  placeholder="给你的漫画起个名字"
                  required
                />
              </div>

              <div>
                <label htmlFor="style" className="block text-sm font-semibold text-gray-700 mb-2">
                  漫画风格
                </label>
                <select
                  id="style"
                  value={formData.style}
                  onChange={(e) => setFormData({ ...formData, style: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 outline-none"
                >
                  <option value="anime">日式动漫</option>
                  <option value="american">美式漫画</option>
                  <option value="chinese">国漫风格</option>
                  <option value="watercolor">水彩风格</option>
                </select>
              </div>

              <div>
                <label htmlFor="panels" className="block text-sm font-semibold text-gray-700 mb-2">
                  分镜数量
                </label>
                <input
                  type="range"
                  id="panels"
                  min="2"
                  max="8"
                  value={formData.panels}
                  onChange={(e) => setFormData({ ...formData, panels: parseInt(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>2 格</span>
                  <span className="font-semibold text-blue-600">{formData.panels} 格</span>
                  <span>8 格</span>
                </div>
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-2">
                  故事描述
                </label>
                <textarea
                  id="description"
                  rows={6}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 outline-none resize-none"
                  placeholder="描述你想要创作的漫画故事情节，例如：一个少年在森林中发现了一只受伤的小精灵..."
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isGenerating || !user || (user.balance || 0) <= 0}
                className="w-full relative group overflow-hidden px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-700 via-cyan-700 to-teal-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <span className="relative flex items-center justify-center">
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      生成中...
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
                      <span className="mr-2">🎬</span>
                      开始创作
                    </>
                  )}
                </span>
              </button>
            </form>
          </div>

          {/* 右侧预览 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <h3 className="text-xl font-bold mb-6 text-gray-900">预览结果</h3>
            {result ? (
              <div className="space-y-4">
                <div className="relative overflow-hidden rounded-2xl">
                  <img 
                    src={result.image} 
                    alt={result.title}
                    className="w-full h-auto object-cover"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">{result.title}</h4>
                    <p className="text-sm text-gray-600">{result.panels} 格漫画</p>
                  </div>
                  <button className="px-6 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-medium hover:shadow-lg transition-shadow">
                    下载
                  </button>
                </div>
              </div>
            ) : (
              <div className="h-96 flex flex-col items-center justify-center text-gray-400">
                <span className="text-6xl mb-4">🎬</span>
                <p>填写左侧表单后，AI 将为你生成漫画</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ComicCreatePage;