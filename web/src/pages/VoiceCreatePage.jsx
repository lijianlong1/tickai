import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useUser } from '../contexts/UserContext';

function VoiceCreatePage() {
  const { user } = useUser();
  const [formData, setFormData] = useState({
    text: '',
    voice: 'zh-CN',
    speed: 1,
    pitch: 1
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const synthRef = useRef(null);
  const speechRef = useRef(null);
  const audioBlobRef = useRef(null);

  useEffect(() => {
    const savedHistory = localStorage.getItem('voiceHistory');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }

    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      const loadVoices = () => {
        const voices = synthRef.current.getVoices();
        setAvailableVoices(voices);
      };
      loadVoices();
      synthRef.current.addEventListener('voiceschanged', loadVoices);
      return () => {
        if (synthRef.current) {
          synthRef.current.removeEventListener('voiceschanged', loadVoices);
        }
      };
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.text.trim()) return;

    setIsGenerating(true);

    try {
      if (!('speechSynthesis' in window)) {
        throw new Error('浏览器不支持语音合成');
      }

      if (speechRef.current) {
        synthRef.current.cancel();
      }

      const utterance = new SpeechSynthesisUtterance(formData.text);
      utterance.lang = formData.voice;
      utterance.rate = formData.speed;
      utterance.pitch = formData.pitch;

      const selectedVoice = availableVoices.find(v => v.lang === formData.voice);
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }

      utterance.onend = () => {
        setIsPlaying(false);
        setIsGenerating(false);
      };

      utterance.onerror = () => {
        setIsPlaying(false);
        setIsGenerating(false);
        alert('语音合成失败，请重试');
      };

      const newHistoryItem = {
        id: Date.now(),
        text: formData.text,
        voice: formData.voice,
        speed: formData.speed,
        pitch: formData.pitch,
        timestamp: new Date().toLocaleString('zh-CN')
      };

      const updatedHistory = [newHistoryItem, ...history].slice(0, 20);
      setHistory(updatedHistory);
      localStorage.setItem('voiceHistory', JSON.stringify(updatedHistory));

      setCurrentAudio({
        text: formData.text,
        voice: formData.voice,
        speed: formData.speed,
        pitch: formData.pitch,
        timestamp: new Date().toLocaleString('zh-CN')
      });

      speechRef.current = utterance;
      synthRef.current.speak(utterance);
      setIsPlaying(true);
      setIsGenerating(false);
    } catch (error) {
      console.error('Error generating speech:', error);
      setIsGenerating(false);
      alert('语音合成失败，请重试');
    }
  };

  const handlePlay = () => {
    if (!('speechSynthesis' in window)) return;

    if (isPlaying) {
      synthRef.current.pause();
      setIsPlaying(false);
    } else {
      synthRef.current.resume();
      setIsPlaying(true);
    }
  };

  const handleStop = () => {
    if (!('speechSynthesis' in window)) return;

    synthRef.current.cancel();
    setIsPlaying(false);
  };

  const handleDownload = async () => {
    if (!currentAudio || !('speechSynthesis' in window)) return;

    try {
      const utterance = new SpeechSynthesisUtterance(currentAudio.text);
      utterance.lang = currentAudio.voice;
      utterance.rate = currentAudio.speed;
      utterance.pitch = currentAudio.pitch;

      const selectedVoice = availableVoices.find(v => v.lang === currentAudio.voice);
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `voice_${Date.now()}.wav`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      synthRef.current.speak(utterance);

      utterance.onend = () => {
        setTimeout(() => {
          mediaRecorder.stop();
        }, 1000);
      };
    } catch (error) {
      console.error('Download error:', error);
      alert('下载失败，请重试');
    }
  };

  const handleHistoryPlay = (item) => {
    if (!('speechSynthesis' in window)) return;

    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(item.text);
    utterance.lang = item.voice;
    utterance.rate = item.speed;
    utterance.pitch = item.pitch;

    const selectedVoice = availableVoices.find(v => v.lang === item.voice);
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    utterance.onend = () => {
      setIsPlaying(false);
    };

    setCurrentAudio({
      text: item.text,
      voice: item.voice,
      speed: item.speed,
      pitch: item.pitch,
      timestamp: item.timestamp
    });

    speechRef.current = utterance;
    synthRef.current.speak(utterance);
    setIsPlaying(true);
  };

  const handleHistoryDownload = async (item) => {
    if (!('speechSynthesis' in window)) return;

    try {
      const utterance = new SpeechSynthesisUtterance(item.text);
      utterance.lang = item.voice;
      utterance.rate = item.speed;
      utterance.pitch = item.pitch;

      const selectedVoice = availableVoices.find(v => v.lang === item.voice);
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `voice_${item.id}.wav`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      synthRef.current.speak(utterance);

      utterance.onend = () => {
        setTimeout(() => {
          mediaRecorder.stop();
        }, 1000);
      };
    } catch (error) {
      console.error('Download error:', error);
      alert('下载失败，请重试');
    }
  };

  const handleDeleteHistory = (id) => {
    const updatedHistory = history.filter(item => item.id !== id);
    setHistory(updatedHistory);
    localStorage.setItem('voiceHistory', JSON.stringify(updatedHistory));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 relative overflow-hidden">
      <Navbar />
      
      <div className="absolute top-20 left-10 w-96 h-96 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-20 left-1/2 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 container mx-auto px-6 pt-24 pb-20">
        <Link to="/create" className="inline-flex items-center text-gray-600 hover:text-indigo-600 mb-8 transition-colors">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回创作中心
        </Link>

        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-indigo-100 to-purple-100 border border-indigo-200 text-indigo-700 text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-indigo-500 rounded-full mr-2 animate-pulse"></span>
            AI 语音合成
          </div>
          <h1 className="text-5xl font-black mb-6">
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              文字转语音
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            使用浏览器内置语音合成，高质量语音，支持下载
          </p>
        </div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="text" className="block text-sm font-semibold text-gray-700 mb-2">
                  输入文本
                </label>
                <textarea
                  id="text"
                  rows={6}
                  value={formData.text}
                  onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300 outline-none resize-none"
                  placeholder="输入你想要转换为语音的文字，例如：欢迎使用 Tick-AI，这是一个强大的人工智能创作平台..."
                  required
                />
                <p className="text-xs text-gray-500 mt-1">字符数：{formData.text.length}</p>
              </div>

              <div>
                <label htmlFor="voice" className="block text-sm font-semibold text-gray-700 mb-2">
                  选择语音
                </label>
                <select
                  id="voice"
                  value={formData.voice}
                  onChange={(e) => setFormData({ ...formData, voice: e.target.value })}
                  className="w-full px-5 py-4 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300 outline-none"
                >
                  {availableVoices.map((voice) => (
                    <option key={voice.lang} value={voice.lang}>
                      {voice.name} ({voice.lang})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="speed" className="block text-sm font-semibold text-gray-700 mb-2">
                  语速调节
                </label>
                <input
                  type="range"
                  id="speed"
                  min="0.1"
                  max="10"
                  step="0.1"
                  value={formData.speed}
                  onChange={(e) => setFormData({ ...formData, speed: parseFloat(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>慢速</span>
                  <span className="font-semibold text-indigo-600">{formData.speed.toFixed(1)}</span>
                  <span>快速</span>
                </div>
              </div>

              <div>
                <label htmlFor="pitch" className="block text-sm font-semibold text-gray-700 mb-2">
                  音调调节
                </label>
                <input
                  type="range"
                  id="pitch"
                  min="0"
                  max="2"
                  step="0.1"
                  value={formData.pitch}
                  onChange={(e) => setFormData({ ...formData, pitch: parseFloat(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>低沉</span>
                  <span className="font-semibold text-indigo-600">{formData.pitch.toFixed(1)}</span>
                  <span>高亢</span>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={isGenerating || !formData.text.trim() || !user || (user.balance || 0) <= 0}
                  className="flex-1 relative group overflow-hidden px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600"></div>
                  <div className="absolute inset-0 bg-gradient-to-r from-indigo-700 via-purple-700 to-pink-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <span className="relative flex items-center justify-center">
                    {isGenerating ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                        合成中...
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
                        <span className="mr-2">🎤</span>
                        开始合成
                      </>
                    )}
                  </span>
                </button>

                {isPlaying && (
                  <button
                    type="button"
                    onClick={handleStop}
                    className="px-8 py-4 rounded-xl bg-red-600 text-white font-semibold hover:bg-red-700 transition-colors"
                  >
                    停止
                  </button>
                )}
              </div>
            </form>

            {currentAudio && (
              <div className="mt-8 p-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100">
                <h3 className="text-lg font-bold mb-4 text-gray-900">当前音频</h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <button
                      onClick={handlePlay}
                      className="w-14 h-14 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-center hover:shadow-lg transition-shadow"
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
                    <div className="flex-1">
                      <p className="text-sm text-gray-600">文本内容</p>
                      <p className="font-medium text-gray-900">{currentAudio.text.substring(0, 50)}...</p>
                    </div>
                    <button
                      onClick={handleDownload}
                      className="px-6 py-3 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 text-white font-medium hover:shadow-lg transition-shadow flex items-center gap-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      下载 MP3
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="text-gray-500">语音：</span>
                      <span className="font-medium text-gray-900">{currentAudio.voice}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">时间：</span>
                      <span className="font-medium text-gray-900">{currentAudio.timestamp}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">语速：</span>
                      <span className="font-medium text-gray-900">{currentAudio.speed}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">历史记录</h3>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="text-indigo-600 hover:text-indigo-700 font-medium text-sm"
              >
                {showHistory ? '收起' : '展开'}
              </button>
            </div>

            {history.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <span className="text-4xl mb-4 block">📝</span>
                <p>暂无历史记录</p>
              </div>
            ) : (
              <div className={`space-y-4 ${showHistory ? 'max-h-[600px] overflow-y-auto' : 'max-h-96 overflow-y-auto'}`}>
                {history.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:shadow-md transition-shadow"
                  >
                    <p className="text-sm text-gray-900 mb-2 line-clamp-2">{item.text}</p>
                    <div className="flex items-center justify-between text-xs text-gray-600 mb-3">
                      <span>{item.voice}</span>
                      <span>{item.timestamp}</span>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleHistoryPlay(item)}
                        className="flex-1 px-3 py-2 rounded-lg bg-indigo-100 text-indigo-700 font-medium text-sm hover:bg-indigo-200 transition-colors"
                      >
                        播放
                      </button>
                      <button
                        onClick={() => handleHistoryDownload(item)}
                        className="px-3 py-2 rounded-lg bg-green-100 text-green-700 font-medium text-sm hover:bg-green-200 transition-colors"
                      >
                        下载
                      </button>
                      <button
                        onClick={() => handleDeleteHistory(item.id)}
                        className="px-3 py-2 rounded-lg bg-red-100 text-red-700 font-medium text-sm hover:bg-red-200 transition-colors"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {history.length > 0 && (
              <button
                onClick={() => {
                  setHistory([]);
                  localStorage.removeItem('voiceHistory');
                }}
                className="w-full mt-4 px-4 py-2 rounded-lg border-2 border-red-200 text-red-600 font-medium hover:bg-red-50 transition-colors"
              >
                清空历史
              </button>
            )}
          </div>
        </div>

        <div className="max-w-6xl mx-auto mt-8 bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
          <h3 className="text-xl font-bold mb-4 text-gray-900">功能特点</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                <span className="text-xl">🎤</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">高质量语音</h4>
                <p className="text-sm text-gray-600">浏览器内置语音合成，音质自然流畅</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                <span className="text-xl">💰</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">完全免费</h4>
                <p className="text-sm text-gray-600">无需 API 密钥，无限制使用</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center flex-shrink-0">
                <span className="text-xl">📥</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">支持下载</h4>
                <p className="text-sm text-gray-600">下载 MP3 格式，永久保存</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <span className="text-xl">🌍</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">多语言支持</h4>
                <p className="text-sm text-gray-600">中文、英文语音合成</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VoiceCreatePage;