import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';

function Navbar() {
  const { user, logout } = useUser();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    setIsMenuOpen(false);
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* 左侧：Logo 和主页链接 */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-500"></div>
              <div className="relative text-2xl font-black bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Tick-AI
              </div>
            </div>
          </Link>

          {/* 中间：导航链接 */}
          <div className="hidden md:flex items-center gap-6">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                isActive('/')
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              主页
            </Link>
            <Link
              to="/create"
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                isActive('/create')
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              创作中心
            </Link>
            <Link
              to="/community"
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                isActive('/community')
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              社区
            </Link>
            <Link
              to="/settings"
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                isActive('/settings')
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              设置
            </Link>
          </div>

          {/* 右侧：用户信息 */}
          {user ? (
            <div className="flex items-center gap-4">
              {/* 账户余额 */}
              <div className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-100">
                <span className="text-sm text-gray-600">余额:</span>
                <span className="font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  ¥{user.balance.toFixed(2)}
                </span>
              </div>

              {/* 用户信息 */}
              <div className="hidden md:flex items-center gap-3 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-100">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center text-xl shadow-md">
                  {user.avatar}
                </div>
                <div className="text-left">
                  <p className="text-sm font-semibold text-gray-900">{user.username}</p>
                  <p className="text-xs text-gray-600">@{user.account}</p>
                </div>
              </div>

              {/* 退出登录按钮 */}
              <button
                onClick={handleLogout}
                className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-red-500 to-pink-500 text-white font-medium shadow-lg hover:shadow-xl transition-all duration-300"
              >
                退出登录
              </button>

              {/* 移动端菜单按钮 */}
              <button
                className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          ) : (
            <Link to="/login" className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium shadow-lg hover:shadow-xl transition-all duration-300">
              登录
            </Link>
          )}
        </div>

        {/* 移动端导航菜单 */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <Link
              to="/"
              className={`block px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                isActive('/')
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              主页
            </Link>
            <Link
              to="/create"
              className={`block px-4 py-2 rounded-lg font-medium transition-all duration-300 mt-2 ${
                isActive('/create')
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              创作中心
            </Link>
            <Link
              to="/community"
              className={`block px-4 py-2 rounded-lg font-medium transition-all duration-300 mt-2 ${
                isActive('/community')
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              社区
            </Link>
            <Link
              to="/settings"
              className={`block px-4 py-2 rounded-lg font-medium transition-all duration-300 mt-2 ${
                isActive('/settings')
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              设置
            </Link>
            {user && (
              <button
                onClick={() => {
                  handleLogout();
                  setIsMenuOpen(false);
                }}
                className="block w-full text-left px-4 py-2 rounded-lg font-medium mt-2 text-red-600 hover:bg-red-50 transition-all duration-300"
              >
                退出登录
              </button>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;