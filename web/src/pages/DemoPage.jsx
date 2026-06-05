import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

function DemoPage() {
  const [activeStep, setActiveStep] = useState(1);

  const steps = [
    {
      id: 1,
      title: '选择创作工具',
      description: '根据你的需求选择合适的 AI 创作工具',
      icon: '1️⃣',
      details: '我们提供多种 AI 创作工具，包括漫剧制作、图片生成、文本创作和语音合成。'
    },
    {
      id: 2,
      title: '输入创作内容',
      description: '输入你的创意想法或文字描述',
      icon: '2️⃣',
      details: '简单描述你想要创作的内容，AI 会根据你的输入生成高质量的作品。'
    },
    {
      id: 3,
      title: 'AI 智能生成',
      description: 'AI 自动处理并生成作品',
      icon: '3️⃣',
      details: '我们的 AI 引擎会在几秒钟内为你生成专业的创作内容。'
    },
    {
      id: 4,
      title: '预览和下载',
      description: '预览结果并下载你的作品',
      icon: '4️⃣',
      details: '对生成的内容进行预览，满意后可以直接下载使用。'
    }
  ];

  const demos = [
    {
      id: 1,
      title: 'AI 漫剧制作演示',
      description: '从文字到漫画的完整流程',
      image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=AI%20comic%20creation%20process%20step%20by%20step%20illustration%20modern%20design&image_size=landscape_16_9',
      type: 'comic'
    },
    {
      id: 2,
      title: 'AI 图片生成演示',
      description: '文字描述转换为精美图片',
      image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=AI%20image%20generation%20showcase%20beautiful%20artwork%20from%20text%20modern%20interface&image_size=landscape_16_9',
      type: 'image'
    },
    {
      id: 3,
      title: 'AI 文本创作演示',
      description: '智能生成各类文本内容',
      image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=AI%20writing%20assistant%20creating%20content%20modern%20workspace%20clean%20design&image_size=landscape_16_9',
      type: 'text'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 relative overflow-hidden">
      <Navbar />
      
      {/* 背景装饰 */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 container mx-auto px-6 pt-24 pb-20">
        {/* 页面标题 */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 border border-purple-200 text-purple-700 text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-2 animate-pulse"></span>
            演示教程
          </div>
          <h1 className="text-5xl sm:text-6xl font-black mb-6">
            <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
              快速上手指南
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            通过简单的演示，快速掌握 AI 创作工具的使用方法
          </p>
        </div>

        {/* 使用步骤 */}
        <div className="max-w-5xl mx-auto mb-20">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">使用步骤</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {steps.map((step) => (
              <div
                key={step.id}
                className={`cursor-pointer transition-all duration-300 ${activeStep === step.id ? 'scale-105' : ''}`}
                onClick={() => setActiveStep(step.id)}
              >
                <div className={`bg-white rounded-2xl p-6 shadow-lg border-2 transition-all duration-300 ${
                  activeStep === step.id ? 'border-purple-500 shadow-purple-200' : 'border-gray-100 hover:border-purple-200'
                }`}>
                  <div className="text-4xl mb-4">{step.icon}</div>
                  <h3 className="text-lg font-bold mb-2 text-gray-900">{step.title}</h3>
                  <p className="text-sm text-gray-600">{step.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* 步骤详情 */}
          <div className="mt-8 bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
            <div className="flex items-center mb-4">
              <span className="text-4xl mr-4">{steps[activeStep - 1].icon}</span>
              <h3 className="text-2xl font-bold text-gray-900">{steps[activeStep - 1].title}</h3>
            </div>
            <p className="text-gray-600 text-lg">{steps[activeStep - 1].details}</p>
          </div>
        </div>

        {/* 演示视频 */}
        <div className="max-w-5xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">功能演示</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {demos.map((demo) => (
              <div key={demo.id} className="group">
                <div className="relative overflow-hidden rounded-2xl shadow-xl border border-gray-100">
                  <img 
                    src={demo.image} 
                    alt={demo.title}
                    className="w-full h-48 object-cover transform group-hover:scale-110 transition duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-6">
                    <div className="text-white">
                      <h3 className="text-lg font-bold">{demo.title}</h3>
                      <p className="text-sm text-gray-200">{demo.description}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA 按钮 */}
        <div className="text-center">
          <Link
            to="/create"
            className="inline-block relative group overflow-hidden px-10 py-5 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-105"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600"></div>
            <div className="absolute inset-0 bg-gradient-to-r from-purple-700 via-pink-700 to-blue-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <span className="relative text-lg">立即开始创作</span>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default DemoPage;