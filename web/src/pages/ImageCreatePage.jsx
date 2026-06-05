import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useUser } from '../contexts/UserContext';

function ImageCreatePage() {
  const { user } = useUser();
  const [formData, setFormData] = useState({
    prompt: '',
    style: 'realistic',
    size: '1024x1024',
    numImages: 1
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [results, setResults] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    
    // TODO: 这里后续接入真实的 AI 图片生成 API
    setTimeout(() => {
      const newResults = Array.from({ length: formData.numImages }, (_, i) => ({
        id: Date.now() + i,
        image: `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(formData.prompt)}%20${formData.style}%20style%20high%20quality&image_size=landscape_16_9`,
        prompt: formData.prompt
      }));
      setResults(newResults);
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 relative overflow-hidden">
      <Navbar />
      
      {/* 背景装饰 */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-rose-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

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
            AI 图片生成
          </div>
          <h1 className="text-5xl font-black mb-6">
            <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-rose-600 bg-clip-text text-transparent">
              文字转图片
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            输入描述文字，AI 为你生成精美的图片
          </p>
        </div>

        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧表单 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="prompt" className="block text-sm font-semibold text-gray-700 mb-2">
                  图片描述
                </label>
                <textarea
                  id="prompt"
                  rows={4}
                  value={formData.prompt}
                  onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 outline-none resize-none"
                  placeholder="描述你想要生成的图片，例如：一只可爱的橘猫坐在窗台上，阳光洒在它身上，温馨的室内场景..."
                  required
                />
              </div>

              <div>
                <label htmlFor="style" className="block text-sm font-semibold text-gray-700 mb-2">
                  图片风格
                </label>
                <select
                  id="style"
                  value={formData.style}
                  onChange={(e) => setFormData({ ...formData, style: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 outline-none"
                >
                  <option value="realistic">写实风格</option>
                  <option value="anime">动漫风格</option>
                  <option value="oil-painting">油画风格</option>
                  <option value="watercolor">水彩风格</option>
                  <option value="3d">3D 渲染</option>
                  <option value="pixel">像素风格</option>
                </select>
              </div>

              <div>
                <label htmlFor="size" className="block text-sm font-semibold text-gray-700 mb-2">
                  图片尺寸
                </label>
                <select
                  id="size"
                  value={formData.size}
                  onChange={(e) => setFormData({ ...formData, size: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 outline-none"
                >
                  <option value="512x512">512 x 512</option>
                  <option value="1024x1024">1024 x 1024</option>
                  <option value="1024x768">1024 x 768 (横向)</option>
                  <option value="768x1024">768 x 1024 (纵向)</option>
                </select>
              </div>

              <div>
                <label htmlFor="numImages" className="block text-sm font-semibold text-gray-700 mb-2">
                  生成数量
                </label>
                <div className="flex gap-2">
                  {[1, 2, 4].map((num) => (
                    <button
                      key={num}
                      type="button"
                      onClick={() => setFormData({ ...formData, numImages: num })}
                      className={`flex-1 py-3 rounded-lg font-medium transition-all duration-300 ${
                        formData.numImages === num
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {num} 张
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={isGenerating || !user || (user.balance || 0) <= 0}
                className="w-full relative group overflow-hidden px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-rose-600"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-700 via-pink-700 to-rose-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
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
                      <span className="mr-2">🖼️</span>
                      开始生成
                    </>
                  )}
                </span>
              </button>
            </form>
          </div>

          {/* 右侧预览 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <h3 className="text-xl font-bold mb-6 text-gray-900">生成结果</h3>
            {results.length > 0 ? (
              <div className={`grid gap-4 ${results.length === 1 ? 'grid-cols-1' : results.length === 2 ? 'grid-cols-2' : 'grid-cols-2'}`}>
                {results.map((result) => (
                  <div key={result.id} className="group relative overflow-hidden rounded-2xl">
                    <img 
                      src={result.image} 
                      alt={result.prompt}
                      className="w-full h-48 object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-2">
                      <button className="px-4 py-2 rounded-lg bg-white text-gray-900 font-medium hover:bg-gray-100 transition-colors">
                        下载
                      </button>
                      <button className="px-4 py-2 rounded-lg bg-white text-gray-900 font-medium hover:bg-gray-100 transition-colors">
                        收藏
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-96 flex flex-col items-center justify-center text-gray-400">
                <span className="text-6xl mb-4">🖼️</span>
                <p>填写左侧表单后，AI 将为你生成图片</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ImageCreatePage;