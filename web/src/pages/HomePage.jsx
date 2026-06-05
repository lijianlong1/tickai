import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import Navbar from '../components/Navbar';
import { useLocation } from 'react-router-dom';

function HomePage() {
  const { user } = useUser();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(true);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState('home');
  const [tips, setTips] = useState([]);
  const sectionRefs = useRef({});

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const carouselImages = [
    {
      url: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=futuristic%20AI%20creativity%20workspace%20with%20holographic%20interfaces%20modern%20design%20purple%20and%20blue%20lighting&image_size=landscape_16_9',
      title: 'AI 创作空间',
      tip: '💡 每日副业技巧：利用 AI 工具批量生成社交媒体内容，提高创作效率'
    },
    {
      url: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=modern%20digital%20marketing%20workspace%20with%20multiple%20screens%20showing%20analytics%20professional&image_size=landscape_16_9',
      title: '数字营销',
      tip: '💡 每日副业技巧：使用 AI 生成营销文案，节省 80% 的内容创作时间'
    },
    {
      url: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=creative%20design%20studio%20with%20colorful%20artwork%20and%20digital%20tools%20artistic%20vibrant&image_size=landscape_16_9',
      title: '创意设计',
      tip: '💡 每日副业技巧：AI 图片生成可以帮助你快速创建产品原型和概念图'
    },
    {
      url: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=content%20creator%20workspace%20with%20camera%20equipment%20and%20editing%20software%20professional&image_size=landscape_16_9',
      title: '内容创作',
      tip: '💡 每日副业技巧：结合 AI 文本和语音工具，打造自动化内容生产流程'
    },
    {
      url: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=freelancer%20home%20office%20setup%20with%20laptop%20and%20coffee%20cozy%20productive&image_size=landscape_16_9',
      title: '自由职业',
      tip: '💡 每日副业技巧：利用 AI 工具承接更多项目，提高收入上限'
    }
  ];

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
      
      const scrollPosition = window.scrollY + 100;
      Object.entries(sectionRefs.current).forEach(([id, ref]) => {
        if (ref && ref.offsetTop <= scrollPosition && ref.offsetTop + ref.offsetHeight > scrollPosition) {
          setActiveSection(id);
        }
      });
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % carouselImages.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // TODO: 这里后续接入真实的副业技巧爬取 API
    setTips([
      '💡 利用 AI 批量生成短视频脚本，提高内容产出效率',
      '💡 使用 AI 图片工具为客户快速生成设计初稿',
      '💡 AI 语音合成可以帮助你制作多语言内容',
      '💡 结合 AI 文本工具，打造自动化客服系统',
      '💡 利用 AI 数据分析工具，发现更多商业机会'
    ]);
  }, []);

  const features = [
    {
      id: 1,
      title: 'AI 漫剧制作',
      description: '使用人工智能技术创作精彩的漫画和动画剧集，释放你的创意潜能',
      icon: '🎬',
      gradient: 'from-blue-500 via-cyan-500 to-teal-500',
      shadow: 'shadow-blue-500/25',
      link: '/create/comic'
    },
    {
      id: 2,
      title: 'AI 图片生成',
      description: '根据文字描述生成高质量图片，支持多种风格和场景',
      icon: '🖼️',
      gradient: 'from-purple-500 via-pink-500 to-rose-500',
      shadow: 'shadow-purple-500/25',
      link: '/create/image'
    },
    {
      id: 3,
      title: 'AI 文本创作',
      description: '智能生成文章、故事、诗歌等各种类型的文本内容',
      icon: '📝',
      gradient: 'from-amber-500 via-orange-500 to-red-500',
      shadow: 'shadow-amber-500/25',
      link: '/create/text'
    },
    {
      id: 4,
      title: 'AI 语音合成',
      description: '将文字转换为自然流畅的语音，支持多种语言和音色',
      icon: '🎤',
      gradient: 'from-indigo-500 via-purple-500 to-pink-500',
      shadow: 'shadow-indigo-500/25',
      link: '/create/voice'
    },
    {
      id: 5,
      title: 'AI 音乐创作',
      description: '描述你想要的音乐风格，AI 为你创作独特的音乐作品',
      icon: '🎵',
      gradient: 'from-purple-500 via-pink-500 to-indigo-500',
      shadow: 'shadow-purple-500/25',
      link: '/create/music'
    },
    {
      id: 6,
      title: 'AI 视频编辑',
      description: '智能视频剪辑和处理，让你的视频作品更加专业',
      icon: '🎥',
      gradient: 'from-red-500 via-rose-500 to-pink-500',
      shadow: 'shadow-red-500/25',
      link: '/create/video'
    }
  ];

  const communityWorks = [
    {
      id: 1,
      title: '梦幻森林',
      author: '创作者小明',
      avatar: '👨‍🎨',
      image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=dreamy%20magical%20forest%20with%20glowing%20trees%20fantasy%20art%20colorful&image_size=landscape_16_9',
      likes: 256
    },
    {
      id: 2,
      title: '科幻城市',
      author: '创作者小红',
      avatar: '👩‍🎨',
      image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=futuristic%20sci-fi%20city%20with%20flying%20cars%20neon%20lights%20cyberpunk&image_size=landscape_16_9',
      likes: 512
    },
    {
      id: 3,
      title: '可爱猫咪漫画',
      author: '创作者小李',
      avatar: '🧑‍🎨',
      image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cat%20manga%20comic%20strip%20funny%20kawaii%20style&image_size=landscape_16_9',
      likes: 384
    }
  ];

  if (isLoading) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 z-50">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-xl opacity-75 animate-pulse"></div>
          <div className="relative w-20 h-20 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-gray-900 overflow-x-hidden">
      <Navbar />
      
      <div 
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(99, 102, 241, 0.1), transparent 50%)`
        }}
      ></div>

      <section 
        id="home" 
        ref={el => sectionRefs.current['home'] = el}
        className="pt-20 pb-24 px-6 relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50"></div>
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
        
        {user && (
          <div className="container mx-auto max-w-7xl relative z-10 mb-8">
            <div className="bg-white rounded-2xl shadow-2xl p-6 border border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center text-2xl shadow-md">
                    {user.avatar}
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">欢迎回来，</p>
                    <p className="text-lg font-bold text-gray-900">{user.username}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">邮箱</p>
                  <p className="text-lg font-bold text-gray-900">{user.email}</p>
                  <p className="text-sm text-gray-600 mt-2">创作点剩余</p>
                  <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {user.balance}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div className="container mx-auto max-w-7xl relative z-10">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-16">
            <div className="w-full lg:w-1/2 space-y-8">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 text-blue-700 text-sm font-medium">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
                探索 AI 创作的未来
              </div>
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black leading-tight">
                <span className="text-gray-900">释放 AI 创作的</span>
                <br />
                <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  无限可能
                </span>
              </h1>
              <p className="text-xl text-gray-600 max-w-lg leading-relaxed">
                利用先进的人工智能技术，释放你的创造力，轻松制作专业级的漫画、图片、文本和更多内容
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/create" className="group relative px-8 py-4 rounded-xl font-semibold text-white overflow-hidden transition-all duration-300 hover:scale-105 text-center">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600"></div>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-700 via-purple-700 to-pink-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <div className="absolute inset-0 shadow-2xl shadow-blue-500/50 group-hover:shadow-blue-500/75 transition-shadow"></div>
                  <span className="relative">开始创作</span>
                </Link>
                <Link to="/demo" className="group px-8 py-4 rounded-xl border-2 border-gray-200 text-gray-700 font-semibold hover:border-gray-300 hover:bg-gray-50 transition-all duration-300 flex items-center justify-center gap-2">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  观看演示
                </Link>
                {!user && (
                  <Link to="/login" className="group px-8 py-4 rounded-xl border-2 border-blue-200 text-blue-700 font-semibold hover:border-blue-300 hover:bg-blue-50 transition-all duration-300 flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                    登录
                  </Link>
                )}
              </div>
              <div className="flex items-center space-x-6 pt-4">
                <div className="flex -space-x-3">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold border-2 border-white shadow-lg">
                      {i}
                    </div>
                  ))}
                </div>
                <div className="text-sm text-gray-600">
                  <span className="font-bold text-gray-900">10,000+</span> 创作者已加入
                </div>
              </div>
            </div>
            <div className="w-full lg:w-1/2">
              <div className="relative group">
                <div className="absolute -inset-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-3xl blur-2xl opacity-25 group-hover:opacity-40 transition duration-1000"></div>
                <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
                  <div className="relative">
                    {carouselImages.map((image, index) => (
                      <div
                        key={index}
                        className={`absolute inset-0 transition-opacity duration-1000 ${
                          index === currentImageIndex ? 'opacity-100' : 'opacity-0'
                        }`}
                      >
                        <img 
                          src={image.url} 
                          alt={image.title}
                          className="w-full h-auto object-cover transform group-hover:scale-105 transition duration-1000" 
                          style={{ maxHeight: '450px' }}
                        />
                      </div>
                    ))}
                    <img 
                      src={carouselImages[currentImageIndex].url} 
                      alt={carouselImages[currentImageIndex].title}
                      className="w-full h-auto object-cover opacity-0" 
                      style={{ maxHeight: '450px' }}
                    />
                  </div>
                  
                  <div className="absolute top-4 right-4 flex gap-2">
                    {carouselImages.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentImageIndex(index)}
                        className={`w-3 h-3 rounded-full transition-all duration-300 ${
                          index === currentImageIndex 
                            ? 'bg-white shadow-lg' 
                            : 'bg-white/50 hover:bg-white/75'
                        }`}
                      />
                    ))}
                  </div>
                  
                  <div className="absolute bottom-6 left-6 right-6 p-5 bg-white/90 backdrop-blur-xl rounded-2xl border border-gray-100 shadow-xl">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm font-semibold text-gray-900">AI 创作工具已就绪</span>
                      </div>
                      <div className="text-xs text-gray-500">实时更新</div>
                    </div>
                    <div className="text-sm text-gray-600 mt-2">
                      {carouselImages[currentImageIndex].tip}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section 
        id="features" 
        ref={el => sectionRefs.current['features'] = el}
        className="py-24 px-6 relative"
      >
        <div className="absolute inset-0 bg-gradient-to-b from-slate-50 to-white"></div>
        <div className="container mx-auto max-w-7xl relative z-10">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 border border-purple-200 text-purple-700 text-sm font-medium mb-6">
              <span className="w-2 h-2 bg-purple-500 rounded-full mr-2 animate-pulse"></span>
              强大的 AI 工具
            </div>
            <h2 className="text-4xl sm:text-5xl font-black mb-6">
              <span className="bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 bg-clip-text text-transparent">
                AI 创作工具
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              探索我们提供的各种 AI 工具，让创作变得更加简单和高效
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <Link 
                key={feature.id} 
                to={feature.link}
                className="group relative"
              >
                <div className={`absolute -inset-0.5 bg-gradient-to-r ${feature.gradient} rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500`}></div>
                <div className="relative bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-500 border border-gray-100">
                  <div className={`bg-gradient-to-r ${feature.gradient} w-16 h-16 rounded-2xl flex items-center justify-center text-white text-3xl mb-6 shadow-lg ${feature.shadow} group-hover:scale-110 transition-transform duration-300`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-gray-900">{feature.title}</h3>
                  <p className="text-gray-600 mb-6 leading-relaxed">{feature.description}</p>
                  <div className="inline-flex items-center text-sm font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent hover:from-blue-700 hover:to-purple-700 transition-all duration-300 group/link">
                    了解更多
                    <svg className="ml-2 w-4 h-4 text-blue-600 transition-transform duration-300 group-hover/link:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section 
        id="community" 
        ref={el => sectionRefs.current['community'] = el}
        className="py-24 px-6 relative"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50"></div>
        <div className="container mx-auto max-w-7xl relative z-10">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 text-blue-700 text-sm font-medium mb-6">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
              创作者社区
            </div>
            <h2 className="text-4xl sm:text-5xl font-black mb-6">
              <span className="bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 bg-clip-text text-transparent">
                社区精选作品
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              探索社区成员的优秀创作，分享你的作品，与创作者们一起成长
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {communityWorks.map((work) => (
              <div key={work.id} className="group">
                <div className="relative bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 hover:shadow-2xl transition-all duration-500">
                  <div className="relative overflow-hidden">
                    <img 
                      src={work.image} 
                      alt={work.title}
                      className="w-full h-64 object-cover transform group-hover:scale-110 transition duration-500"
                    />
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-bold mb-2 text-gray-900">{work.title}</h3>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{work.avatar}</span>
                        <span className="text-sm text-gray-600">{work.author}</span>
                      </div>
                      <span className="flex items-center gap-1 text-sm text-gray-600">
                        <span>❤️</span>
                        <span>{work.likes}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="text-center">
            <Link 
              to="/community" 
              className="inline-flex items-center px-8 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-xl transition-all duration-300"
            >
              探索更多作品
              <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      <section 
        id="about" 
        ref={el => sectionRefs.current['about'] = el}
        className="py-24 px-6 relative"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50"></div>
        <div className="container mx-auto max-w-7xl relative z-10">
          <div className="flex flex-col lg:flex-row items-center gap-16">
            <div className="w-full lg:w-1/2">
              <div className="relative group">
                <div className="absolute -inset-4 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 rounded-3xl blur-2xl opacity-25 group-hover:opacity-40 transition duration-1000"></div>
                <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
                  <img 
                    src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=professional%20AI%20developer%20in%20modern%20tech%20workspace%20with%20purple%20ambient%20lighting%20futuristic%20clean%20minimalist&image_size=portrait_4_3" 
                    alt="关于我" 
                    className="w-full h-auto object-cover transform group-hover:scale-105 transition duration-1000" 
                    style={{ maxHeight: '500px' }}
                  />
                </div>
              </div>
            </div>
            <div className="w-full lg:w-1/2 space-y-8">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 text-blue-700 text-sm font-medium">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
                关于创作者
              </div>
              <h2 className="text-4xl sm:text-5xl font-black">
                <span className="bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 bg-clip-text text-transparent">
                  关于我
                </span>
              </h2>
              <p className="text-xl text-gray-600 leading-relaxed">
                我是一名 AI 技术爱好者和创作者，致力于探索人工智能在创意领域的应用。通过这个平台，我希望能够为更多人提供简单易用的 AI 创作工具，帮助大家释放无限的创造力。
              </p>
              <p className="text-xl text-gray-600 leading-relaxed">
                无论是漫画制作、图片生成还是文本创作，我们的工具都能为你提供强大的支持，让创作过程变得更加高效和有趣。
              </p>
              <div className="flex flex-wrap gap-3 pt-4">
                {['AI 技术', '创意设计', '漫画制作', '内容创作', '技术开发'].map((skill, index) => (
                  <span key={index} className="px-5 py-2.5 rounded-full bg-white text-gray-700 text-sm font-semibold border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-300">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section 
        id="contact" 
        ref={el => sectionRefs.current['contact'] = el}
        className="py-24 px-6 relative"
      >
        <div className="absolute inset-0 bg-gradient-to-b from-white to-slate-50"></div>
        <div className="container mx-auto max-w-5xl relative z-10">
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 text-blue-700 text-sm font-medium mb-6">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
              保持联系
            </div>
            <h2 className="text-4xl sm:text-5xl font-black mb-6">
              <span className="bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 bg-clip-text text-transparent">
                联系我
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              如果你有任何问题或建议，欢迎随时联系我
            </p>
          </div>
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-3xl blur opacity-25 group-hover:opacity-30 transition duration-1000"></div>
            <div className="relative bg-white rounded-3xl p-10 shadow-2xl border border-gray-100">
              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-semibold text-gray-700 mb-2">姓名</label>
                    <input 
                      type="text" 
                      id="name" 
                      className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 outline-none"
                      placeholder="请输入你的姓名"
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">邮箱</label>
                    <input 
                      type="email" 
                      id="email" 
                      className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 outline-none"
                      placeholder="请输入你的邮箱"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="subject" className="block text-sm font-semibold text-gray-700 mb-2">主题</label>
                  <input 
                    type="text" 
                    id="subject" 
                    className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 outline-none"
                    placeholder="请输入主题"
                  />
                </div>
                <div>
                  <label htmlFor="message" className="block text-sm font-semibold text-gray-700 mb-2">消息</label>
                  <textarea 
                    id="message" 
                    rows={5} 
                    className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 outline-none resize-none"
                    placeholder="请输入你的消息"
                  ></textarea>
                </div>
                <button 
                  type="submit" 
                  className="w-full relative group overflow-hidden px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-[1.02]"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600"></div>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-700 via-purple-700 to-pink-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <div className="absolute inset-0 shadow-2xl shadow-blue-500/50 group-hover:shadow-blue-500/75 transition-shadow"></div>
                  <span className="relative">发送消息</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      <footer className="py-16 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10"></div>
        <div className="container mx-auto max-w-7xl relative z-10">
          <div className="flex flex-col lg:flex-row justify-between items-center gap-12">
            <Link to="/" className="text-3xl font-black bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Tick-AI
            </Link>
            <div className="flex flex-wrap justify-center gap-6">
              {[
                { id: 'home', label: '首页' },
                { id: 'features', label: '功能' },
                { id: 'community', label: '社区' },
                { id: 'about', label: '关于' },
                { id: 'contact', label: '联系' }
              ].map((item) => (
                <Link
                  key={item.id}
                  to={`/#${item.id}`}
                  className="px-5 py-2.5 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 transition-all duration-300 font-medium"
                >
                  {item.label}
                </Link>
              ))}
            </div>
            <div className="flex space-x-4">
              {['Twitter', 'GitHub', 'LinkedIn', 'Instagram'].map((social, index) => (
                <a 
                  key={index} 
                  href="#" 
                  className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center hover:bg-gradient-to-r hover:from-blue-600 hover:to-purple-600 transition-all duration-300 backdrop-blur-sm border border-white/10"
                >
                  <span className="text-white font-bold">{social}</span>
                </a>
              ))}
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-white/10 text-center text-gray-400 text-sm">
            © 2026 Tick-AI. 保留所有权利。
          </div>
        </div>
      </footer>
    </div>
  );
}

export default HomePage;