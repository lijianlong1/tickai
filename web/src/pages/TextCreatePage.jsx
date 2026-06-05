import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useUser } from '../contexts/UserContext';

function TextCreatePage() {
  const { user } = useUser();
  const [formData, setFormData] = useState({
    type: 'article',
    topic: '',
    tone: 'professional',
    length: 'medium'
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    
    // TODO: 这里后续接入真实的 AI 文本创作 API
    setTimeout(() => {
      setResult({
        title: `关于"${formData.topic}"的${formData.type === 'article' ? '文章' : formData.type === 'story' ? '故事' : '诗歌'}`,
        content: `这是一个关于"${formData.topic}"的示例文本内容。\n\nAI 将根据你的输入生成高质量的文本内容。这里展示的是占位文本，实际使用时会接入真实的 AI 文本生成接口。\n\n你可以选择不同的文本类型、语气和长度，AI 会为你生成符合要求的文本内容。`,
        wordCount: 256
      });
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 relative overflow-hidden">
      <Navbar />
      
      {/* 背景装饰 */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-amber-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-orange-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-red-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 container mx-auto px-6 pt-24 pb-20">
        {/* 返回按钮 */}
        <Link to="/create" className="inline-flex items-center text-gray-600 hover:text-amber-600 mb-8 transition-colors">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回创作中心
        </Link>

        {/* 页面标题 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-amber-100 to-orange-100 border border-amber-200 text-amber-700 text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-amber-500 rounded-full mr-2 animate-pulse"></span>
            AI 文本创作
          </div>
          <h1 className="text-5xl font-black mb-6">
            <span className="bg-gradient-to-r from-amber-600 via-orange-600 to-red-600 bg-clip-text text-transparent">
              智能文本生成
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            输入主题，AI 为你生成各类文本内容
          </p>
        </div>

        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧表单 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  文本类型
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: 'article', label: '文章' },
                    { value: 'story', label: '故事' },
                    { value: 'poetry', label: '诗歌' }
                  ].map((type) => (
                    <button
                      key={type.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, type: type.value })}
                      className={`py-3 rounded-lg font-medium transition-all duration-300 ${
                        formData.type === type.value
                          ? 'bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-lg'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label htmlFor="topic" className="block text-sm font-semibold text-gray-700 mb-2">
                  主题/关键词
                </label>
                <textarea
                  id="topic"
                  rows={4}
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-amber-500 focus:ring-4 focus:ring-amber-100 transition-all duration-300 outline-none resize-none"
                  placeholder="输入你想要创作的主题或关键词，例如：人工智能的未来发展、一个关于友情的故事..."
                  required
                />
              </div>

              <div>
                <label htmlFor="tone" className="block text-sm font-semibold text-gray-700 mb-2">
                  文本语气
                </label>
                <select
                  id="tone"
                  value={formData.tone}
                  onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-amber-500 focus:ring-4 focus:ring-amber-100 transition-all duration-300 outline-none"
                >
                  <option value="professional">专业正式</option>
                  <option value="casual">轻松随意</option>
                  <option value="creative">创意想象</option>
                  <option value="humorous">幽默风趣</option>
                </select>
              </div>

              <div>
                <label htmlFor="length" className="block text-sm font-semibold text-gray-700 mb-2">
                  文本长度
                </label>
                <div className="flex gap-2">
                  {[
                    { value: 'short', label: '短篇' },
                    { value: 'medium', label: '中篇' },
                    { value: 'long', label: '长篇' }
                  ].map((len) => (
                    <button
                      key={len.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, length: len.value })}
                      className={`flex-1 py-3 rounded-lg font-medium transition-all duration-300 ${
                        formData.length === len.value
                          ? 'bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-lg'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {len.label}
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={isGenerating || !user || (user.balance || 0) <= 0}
                className="w-full relative group overflow-hidden px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-amber-600 via-orange-600 to-red-600"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-amber-700 via-orange-700 to-red-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
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
                      <span className="mr-2">📝</span>
                      开始创作
                    </>
                  )}
                </span>
              </button>
            </form>
          </div>

          {/* 右侧预览 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">生成结果</h3>
              {result && (
                <span className="text-sm text-gray-500">{result.wordCount} 字</span>
              )}
            </div>
            {result ? (
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-gray-900">{result.title}</h4>
                <div className="prose prose-amber max-w-none">
                  <p className="text-gray-700 whitespace-pre-line leading-relaxed">{result.content}</p>
                </div>
                <div className="flex gap-2 pt-4">
                  <button className="flex-1 px-4 py-2 rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 text-white font-medium hover:shadow-lg transition-shadow">
                    复制文本
                  </button>
                  <button className="flex-1 px-4 py-2 rounded-lg border-2 border-gray-200 text-gray-700 font-medium hover:bg-gray-50 transition-colors">
                    下载文档
                  </button>
                </div>
              </div>
            ) : (
              <div className="h-96 flex flex-col items-center justify-center text-gray-400">
                <span className="text-6xl mb-4">📝</span>
                <p>填写左侧表单后，AI 将为你生成文本</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default TextCreatePage;