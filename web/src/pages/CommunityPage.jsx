import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

function CommunityPage() {
  const [activeTab, setActiveTab] = useState('images');
  const [imageWorks, setImageWorks] = useState([]);
  const [videoWorks, setVideoWorks] = useState([]);

  useEffect(() => {
    // TODO: 这里后续接入真实的社区数据 API
    setImageWorks([
      {
        id: 1,
        title: '梦幻森林',
        author: '创作者小明',
        avatar: '👨‍🎨',
        type: 'image',
        image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=dreamy%20magical%20forest%20with%20glowing%20trees%20fantasy%20art%20colorful&image_size=landscape_16_9',
        prompt: 'dreamy magical forest with glowing trees fantasy art colorful',
        model: 'Stable Diffusion XL',
        steps: 50,
        guidance: 7.5,
        likes: 256,
        views: 1024,
        createdAt: '2小时前'
      },
      {
        id: 2,
        title: '科幻城市',
        author: '创作者小红',
        avatar: '👩‍🎨',
        type: 'image',
        image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=futuristic%20sci-fi%20city%20with%20flying%20cars%20neon%20lights%20cyberpunk&image_size=landscape_16_9',
        prompt: 'futuristic sci-fi city with flying cars neon lights cyberpunk',
        model: 'Stable Diffusion XL',
        steps: 50,
        guidance: 7.5,
        likes: 512,
        views: 2048,
        createdAt: '5小时前'
      },
      {
        id: 3,
        title: '可爱猫咪漫画',
        author: '创作者小李',
        avatar: '🧑‍🎨',
        type: 'image',
        image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cat%20manga%20comic%20strip%20funny%20kawaii%20style&image_size=landscape_16_9',
        prompt: 'cute cat manga comic strip funny kawaii style',
        model: 'Stable Diffusion XL',
        steps: 50,
        guidance: 7.5,
        likes: 384,
        views: 1536,
        createdAt: '1天前'
      },
      {
        id: 4,
        title: '星空下的城堡',
        author: '创作者小王',
        avatar: '👨‍🎨',
        type: 'image',
        image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=beautiful%20castle%20under%20starry%20night%20sky%20magical%20fantasy&image_size=landscape_16_9',
        prompt: 'beautiful castle under starry night sky magical fantasy',
        model: 'Stable Diffusion XL',
        steps: 50,
        guidance: 7.5,
        likes: 640,
        views: 2560,
        createdAt: '2天前'
      },
      {
        id: 5,
        title: '海底世界',
        author: '创作者小刘',
        avatar: '👩‍🎨',
        type: 'image',
        image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=underwater%20world%20with%20colorful%20fish%20and%20coral%20reefs%20beautiful&image_size=landscape_16_9',
        prompt: 'underwater world with colorful fish and coral reefs beautiful',
        model: 'Stable Diffusion XL',
        steps: 50,
        guidance: 7.5,
        likes: 768,
        views: 3072,
        createdAt: '4天前'
      },
      {
        id: 6,
        title: '樱花季节',
        author: '创作者小张',
        avatar: '🧑‍🎨',
        type: 'image',
        image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=beautiful%20cherry%20blossom%20season%20pink%20flowers%20spring%20landscape&image_size=landscape_16_9',
        prompt: 'beautiful cherry blossom season pink flowers spring landscape',
        model: 'Stable Diffusion XL',
        steps: 50,
        guidance: 7.5,
        likes: 896,
        views: 3584,
        createdAt: '5天前'
      }
    ]);

    setVideoWorks([
      {
        id: 101,
        title: 'AI 动画短片：机器人冒险',
        author: '创作者小明',
        avatar: '👨‍🎨',
        type: 'video',
        thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=robot%20adventure%20animated%20movie%20poster%20colorful%20fun&image_size=landscape_16_9',
        prompt: 'robot adventure animated movie, colorful, fun story',
        model: 'Runway Gen-2',
        duration: '2:30',
        fps: 24,
        likes: 1024,
        views: 4096,
        createdAt: '1天前'
      },
      {
        id: 102,
        title: '科幻城市漫步',
        author: '创作者小红',
        avatar: '👩‍🎨',
        type: 'video',
        thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=walking%20through%20futuristic%20cyberpunk%20city%20neon%20lights%20night&image_size=landscape_16_9',
        prompt: 'walking through futuristic cyberpunk city neon lights night',
        model: 'Runway Gen-2',
        duration: '1:45',
        fps: 30,
        likes: 1536,
        views: 6144,
        createdAt: '3天前'
      },
      {
        id: 103,
        title: '自然风光延时摄影',
        author: '创作者小李',
        avatar: '🧑‍🎨',
        type: 'video',
        thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=beautiful%20nature%20timelapse%20sunset%20mountains%20clouds%20moving&image_size=landscape_16_9',
        prompt: 'beautiful nature timelapse sunset mountains clouds moving',
        model: 'Pika Labs',
        duration: '0:30',
        fps: 60,
        likes: 2048,
        views: 8192,
        createdAt: '4天前'
      },
      {
        id: 104,
        title: '抽象艺术动画',
        author: '创作者小王',
        avatar: '👨‍🎨',
        type: 'video',
        thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=abstract%20art%20animation%20colorful%20shapes%20morphing%20psychedelic&image_size=landscape_16_9',
        prompt: 'abstract art animation colorful shapes morphing psychedelic',
        model: 'Pika Labs',
        duration: '1:00',
        fps: 24,
        likes: 768,
        views: 3072,
        createdAt: '5天前'
      },
      {
        id: 105,
        title: '梦幻水彩动画',
        author: '创作者小刘',
        avatar: '👩‍🎨',
        type: 'video',
        thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=watercolor%20painting%20animation%20flowing%20colors%20dreamy%20artistic&image_size=landscape_16_9',
        prompt: 'watercolor painting animation flowing colors dreamy artistic',
        model: 'Runway Gen-2',
        duration: '1:20',
        fps: 30,
        likes: 1280,
        views: 5120,
        createdAt: '6天前'
      },
      {
        id: 106,
        title: '粒子特效展示',
        author: '创作者小张',
        avatar: '🧑‍🎨',
        type: 'video',
        thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=particle%20effects%20visualization%20glowing%20dots%20swirling%20magical&image_size=landscape_16_9',
        prompt: 'particle effects visualization glowing dots swirling magical',
        model: 'Pika Labs',
        duration: '0:45',
        fps: 60,
        likes: 896,
        views: 3584,
        createdAt: '7天前'
      }
    ]);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 relative overflow-hidden">
      <Navbar />
      
      {/* 背景装饰 */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 container mx-auto px-6 pt-24 pb-20">
        {/* 页面标题 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 text-blue-700 text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
            创作者社区
          </div>
          <h1 className="text-5xl font-black mb-6">
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              探索创意作品
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            发现优秀作品，分享你的创意，与创作者们一起成长
          </p>
        </div>

        {/* 标签切换 */}
        <div className="flex justify-center mb-12">
          <div className="inline-flex bg-white rounded-2xl p-2 shadow-lg border border-gray-100">
            <button
              onClick={() => setActiveTab('images')}
              className={`px-8 py-3 rounded-xl font-medium transition-all duration-300 ${
                activeTab === 'images'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🖼️ 图片作品
            </button>
            <button
              onClick={() => setActiveTab('videos')}
              className={`px-8 py-3 rounded-xl font-medium transition-all duration-300 ${
                activeTab === 'videos'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🎬 视频作品
            </button>
          </div>
        </div>

        {/* 图片作品展示 */}
        {activeTab === 'images' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {imageWorks.map((work) => (
              <div key={work.id} className="group">
                <div className="relative bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 hover:shadow-2xl transition-all duration-500">
                  <div className="relative overflow-hidden">
                    <img 
                      src={work.image} 
                      alt={work.title}
                      className="w-full h-64 object-cover transform group-hover:scale-110 transition duration-500"
                    />
                    <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-white/90 backdrop-blur-sm text-sm font-medium text-gray-700">
                      🖼️ 图片
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-bold mb-2 text-gray-900">{work.title}</h3>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{work.avatar}</span>
                        <span className="text-sm text-gray-600">{work.author}</span>
                      </div>
                      <span className="text-xs text-gray-500">{work.createdAt}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                          <span>❤️</span>
                          <span>{work.likes}</span>
                        </span>
                        <span className="flex items-center gap-1">
                          <span>👁️</span>
                          <span>{work.views}</span>
                        </span>
                      </div>
                      <Link 
                        to={`/work/${work.id}`}
                        className="text-blue-600 hover:text-blue-700 font-medium"
                      >
                        查看详情
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 视频作品展示 */}
        {activeTab === 'videos' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {videoWorks.map((work) => (
              <div key={work.id} className="group">
                <div className="relative bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 hover:shadow-2xl transition-all duration-500">
                  <div className="relative overflow-hidden">
                    <img 
                      src={work.thumbnail} 
                      alt={work.title}
                      className="w-full h-64 object-cover transform group-hover:scale-110 transition duration-500"
                    />
                    <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center">
                        <svg className="w-8 h-8 text-blue-600 ml-1" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      </div>
                    </div>
                    <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-white/90 backdrop-blur-sm text-sm font-medium text-gray-700">
                      🎬 视频
                    </div>
                    <div className="absolute bottom-4 right-4 px-3 py-1 rounded-full bg-black/70 backdrop-blur-sm text-sm font-medium text-white">
                      {work.duration}
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-bold mb-2 text-gray-900">{work.title}</h3>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{work.avatar}</span>
                        <span className="text-sm text-gray-600">{work.author}</span>
                      </div>
                      <span className="text-xs text-gray-500">{work.createdAt}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                          <span>❤️</span>
                          <span>{work.likes}</span>
                        </span>
                        <span className="flex items-center gap-1">
                          <span>👁️</span>
                          <span>{work.views}</span>
                        </span>
                      </div>
                      <Link 
                        to={`/work/${work.id}`}
                        className="text-blue-600 hover:text-blue-700 font-medium"
                      >
                        查看详情
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 发布作品按钮 */}
        <div className="fixed bottom-8 right-8">
          <button className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 flex items-center justify-center text-3xl">
            +
          </button>
        </div>
      </div>
    </div>
  );
}

export default CommunityPage;