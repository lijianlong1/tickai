import React from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';

function SettingsPage() {
  const { user } = useUser();

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">请先登录</h2>
          <Link to="/login" className="inline-block px-6 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium hover:shadow-xl transition-all duration-300">
            前往登录
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-12 px-6">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-8">
          <Link to="/" className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            返回主页
          </Link>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
          <div className="text-center mb-10">
            <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center text-4xl shadow-xl mb-4">
              {user.avatar}
            </div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
              {user.username}
            </h1>
            <p className="text-gray-600">@{user.account}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-100">
              <p className="text-sm text-gray-600 mb-1">用户名</p>
              <p className="text-xl font-bold text-gray-900">{user.username}</p>
            </div>

            <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-100">
              <p className="text-sm text-gray-600 mb-1">邮箱账号</p>
              <p className="text-xl font-bold text-gray-900">{user.email}</p>
            </div>

            <div className="p-6 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 border border-green-100">
              <p className="text-sm text-gray-600 mb-1">账户余额</p>
              <p className="text-2xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                ¥{user.balance.toFixed(2)}
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-100">
              <p className="text-sm text-gray-600 mb-1">用户 ID</p>
              <p className="text-sm font-mono text-gray-900 truncate" title={user.id}>
                {user.id}
              </p>
            </div>
          </div>

          <div className="mt-8 p-6 rounded-2xl bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">账户设置</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 rounded-xl bg-white border border-gray-200 hover:border-blue-200 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <span className="text-gray-700 font-medium">个人信息</span>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>

              <div className="flex items-center justify-between p-4 rounded-xl bg-white border border-gray-200 hover:border-purple-200 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center text-purple-600">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <span className="text-gray-700 font-medium">安全设置</span>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>

              <div className="flex items-center justify-between p-4 rounded-xl bg-white border border-gray-200 hover:border-pink-200 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-pink-100 flex items-center justify-center text-pink-600">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                  </div>
                  <span className="text-gray-700 font-medium">通知设置</span>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
