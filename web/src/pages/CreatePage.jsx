import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useUser } from '../contexts/UserContext';

function CreatePage() {
  const { user } = useUser();

  const tools = [
    {
      id: 1,
      title: 'AI 漫剧制作',
      description: '创作精彩的漫画和动画剧集',
      icon: '🎬',
      link: '/create/comic',
      gradient: 'from-blue-500 via-cyan-500 to-teal-500',
      shadow: 'shadow-blue-500/25'
    },
    {
      id: 2,
      title: 'AI 图片生成',
      description: '根据文字生成高质量图片',
      icon: '🖼️',
      link: '/create/image',
      gradient: 'from-purple-500 via-pink-500 to-rose-500',
      shadow: 'shadow-purple-500/25'
    },
    {
      id: 3,
      title: 'AI 文本创作',
      description: '智能生成各类文本内容',
      icon: '📝',
      link: '/create/text',
      gradient: 'from-amber-500 via-orange-500 to-red-500',
      shadow: 'shadow-amber-500/25'
    },
    {
      id: 4,
      title: 'AI 语音合成',
      description: '文字转语音，支持多种音色',
      icon: '🎤',
      link: '/create/voice',
      gradient: 'from-indigo-500 via-purple-500 to-pink-500',
      shadow: 'shadow-indigo-500/25'
    },
    {
      id: 5,
      title: 'AI 音乐创作',
      description: '描述风格，AI 创作独特音乐',
      icon: '🎵',
      link: '/create/music',
      gradient: 'from-purple-500 via-pink-500 to-indigo-500',
      shadow: 'shadow-purple-500/25'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 relative overflow-hidden">
      <Navbar />
      
      {/* 背景装饰 */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 container mx-auto px-6 pt-24 pb-20">
        {/* 用户信息卡片 */}
        {user ? (
          <div className="mb-12">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>
              <div className="relative bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
                <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
                  {/* 左侧：用户基本信息 */}
                  <div className="flex items-center gap-6">
                    <div className="relative">
                      <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center text-5xl shadow-xl">
                        {user.avatar || '👨‍🎨'}
                      </div>
                      <div className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-green-500 border-4 border-white flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-3xl font-black text-gray-900">{user.username}</h2>
                        <span className="px-3 py-1 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 text-blue-700 text-sm font-medium">
                          创作者
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-gray-600">
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                          @{user.account || user.email.split('@')[0]}
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          {user.email}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 右侧：统计数据 */}
                  <div className="flex items-center gap-8">
                    {/* 账户余额 */}
                    <div className="text-center">
                      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-100">
                        <p className="text-sm text-gray-600 mb-2">账户余额</p>
                        <p className="text-3xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                          ¥{(user.balance || 0).toFixed(2)}
                        </p>
                      </div>
                    </div>

                    {/* 充值按钮 */}
                    <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg transition-shadow">
                      充值
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="mb-12">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>
              <div className="relative bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
                <div className="flex flex-col items-center text-center gap-4">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center text-4xl shadow-xl">
                    👋
                  </div>
                  <h2 className="text-2xl font-black text-gray-900">欢迎来到创作中心</h2>
                  <p className="text-gray-600">登录后即可开始您的 AI 创作之旅</p>
                  <div className="flex gap-4 mt-2">
                    <Link to="/login" className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg transition-shadow">
                      立即登录
                    </Link>
                    <Link to="/register" className="px-6 py-3 rounded-xl border-2 border-gray-200 text-gray-700 font-semibold hover:border-gray-300 transition-colors">
                      注册账号
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 页面标题 */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 text-blue-700 text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
            AI 创作中心
          </div>
          <h1 className="text-5xl sm:text-6xl font-black mb-6">
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              选择你的创作工具
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            探索强大的 AI 创作工具，让创意变为现实
          </p>
        </div>

        {/* 工具卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {tools.map((tool) => (
            <Link
              key={tool.id}
              to={tool.link}
              className="group relative"
            >
              <div className={`absolute -inset-1 bg-gradient-to-r ${tool.gradient} rounded-3xl blur opacity-0 group-hover:opacity-100 transition duration-500`}></div>
              <div className="relative bg-white rounded-3xl p-10 shadow-xl hover:shadow-2xl transition-all duration-500 border border-gray-100 h-full">
                <div className={`bg-gradient-to-r ${tool.gradient} w-20 h-20 rounded-2xl flex items-center justify-center text-white text-4xl mb-6 shadow-lg ${tool.shadow} group-hover:scale-110 transition-transform duration-300`}>
                  {tool.icon}
                </div>
                <h3 className="text-3xl font-bold mb-4 text-gray-900">{tool.title}</h3>
                <p className="text-gray-600 text-lg mb-6">{tool.description}</p>
                <div className="flex items-center text-blue-600 font-semibold group-hover:text-blue-700 transition-colors">
                  开始创作
                  <svg className="ml-2 w-5 h-5 transition-transform duration-300 group-hover:translate-x-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* 快速开始提示 */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center px-6 py-3 rounded-full bg-white shadow-lg border border-gray-100">
            <span className="text-gray-600">💡</span>
            <span className="ml-2 text-gray-700 font-medium">首次使用？</span>
            <Link to="/demo" className="ml-2 text-blue-600 hover:text-blue-700 font-semibold">
              观看演示教程
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CreatePage;