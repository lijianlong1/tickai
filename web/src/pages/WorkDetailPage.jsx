import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';

function WorkDetailPage() {
  const { id } = useParams();
  const [work, setWork] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    // TODO: 这里后续接入真实的作品详情 API
    // 根据 id 获取作品详情
    setWork({
      id: id,
      title: '梦幻森林',
      author: '创作者小明',
      avatar: '👨‍🎨',
      type: 'image',
      image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=dreamy%20magical%20forest%20with%20glowing%20trees%20fantasy%20art%20colorful&image_size=landscape_16_9',
      prompt: 'dreamy magical forest with glowing trees fantasy art colorful, highly detailed, 8k resolution, cinematic lighting',
      negativePrompt: 'blurry, low quality, distorted, ugly',
      model: 'Stable Diffusion XL',
      steps: 50,
      guidance: 7.5,
      seed: 1234567890,
      sampler: 'DPM++ 2M Karras',
      size: '1024x576',
      likes: 256,
      views: 1024,
      createdAt: '2小时前',
      description: '这是一幅由 AI 生成的梦幻森林场景，展现了神奇的发光树木和绚丽的色彩。作品充满了幻想色彩，适合用作壁纸或插画。'
    });
  }, [id]);

  if (!work) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 relative overflow-hidden">
      <Navbar />
      
      {/* 背景装饰 */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 container mx-auto px-6 pt-24 pb-20">
        {/* 返回按钮 */}
        <Link to="/community" className="inline-flex items-center text-gray-600 hover:text-blue-600 mb-8 transition-colors">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回社区
        </Link>

        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧：作品展示 */}
          <div className="space-y-6">
            <div className="relative group">
              <div className="absolute -inset-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-3xl blur-2xl opacity-25 group-hover:opacity-40 transition duration-1000"></div>
              <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
                {work.type === 'image' ? (
                  <img 
                    src={work.image} 
                    alt={work.title}
                    className="w-full h-auto object-cover"
                  />
                ) : (
                  <div className="relative">
                    <img 
                      src={work.image} 
                      alt={work.title}
                      className="w-full h-auto object-cover"
                    />
                    <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                      <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="w-20 h-20 rounded-full bg-white/90 flex items-center justify-center hover:shadow-lg transition-shadow"
                      >
                        {isPlaying ? (
                          <svg className="w-10 h-10 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                          </svg>
                        ) : (
                          <svg className="w-10 h-10 text-blue-600 ml-1" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 作品信息 */}
            <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
              <h1 className="text-3xl font-black mb-4 text-gray-900">{work.title}</h1>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{work.avatar}</span>
                  <div>
                    <p className="font-semibold text-gray-900">{work.author}</p>
                    <p className="text-sm text-gray-600">{work.createdAt}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <span>❤️</span>
                    <span>{work.likes}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span>👁️</span>
                    <span>{work.views}</span>
                  </span>
                </div>
              </div>
              <p className="text-gray-600 leading-relaxed">{work.description}</p>
            </div>
          </div>

          {/* 右侧：提示词和模型参数 */}
          <div className="space-y-6">
            {/* 提示词 */}
            <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">💡 提示词</h2>
                <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                  复制
                </button>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 mb-4">
                <code className="text-sm text-gray-800 break-words">{work.prompt}</code>
              </div>
              {work.negativePrompt && (
                <>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">反向提示词</h3>
                  <div className="bg-red-50 rounded-xl p-4">
                    <code className="text-sm text-red-800 break-words">{work.negativePrompt}</code>
                  </div>
                </>
              )}
            </div>

            {/* 模型参数 */}
            <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
              <h2 className="text-xl font-bold text-gray-900 mb-4">⚙️ 模型参数</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="text-gray-600">模型</span>
                  <span className="font-semibold text-gray-900">{work.model}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="text-gray-600">采样器</span>
                  <span className="font-semibold text-gray-900">{work.sampler}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="text-gray-600">步数</span>
                  <span className="font-semibold text-gray-900">{work.steps}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="text-gray-600">引导系数</span>
                  <span className="font-semibold text-gray-900">{work.guidance}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="text-gray-600">种子</span>
                  <span className="font-semibold text-gray-900">{work.seed}</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-gray-600">尺寸</span>
                  <span className="font-semibold text-gray-900">{work.size}</span>
                </div>
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-3">
              <button className="flex-1 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg transition-shadow">
                使用此提示词
              </button>
              <button className="px-6 py-3 rounded-xl border-2 border-gray-200 text-gray-700 font-semibold hover:bg-gray-50 transition-colors">
                下载
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WorkDetailPage;