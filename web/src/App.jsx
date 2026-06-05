import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CreatePage from './pages/CreatePage';
import DemoPage from './pages/DemoPage';
import ComicCreatePage from './pages/ComicCreatePage';
import ImageCreatePage from './pages/ImageCreatePage';
import TextCreatePage from './pages/TextCreatePage';
import VoiceCreatePage from './pages/VoiceCreatePage';
import MusicCreatePage from './pages/MusicCreatePage';
import CommunityPage from './pages/CommunityPage';
import WorkDetailPage from './pages/WorkDetailPage';
import SettingsPage from './pages/SettingsPage';
import { UserProvider } from './contexts/UserContext';
import './index.css';

function App() {
  return (
    <UserProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/create" element={<CreatePage />} />
          <Route path="/demo" element={<DemoPage />} />
          <Route path="/create/comic" element={<ComicCreatePage />} />
          <Route path="/create/image" element={<ImageCreatePage />} />
          <Route path="/create/text" element={<TextCreatePage />} />
          <Route path="/create/voice" element={<VoiceCreatePage />} />
          <Route path="/create/music" element={<MusicCreatePage />} />
          <Route path="/community" element={<CommunityPage />} />
          <Route path="/work/:id" element={<WorkDetailPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Router>
    </UserProvider>
  );
}

export default App;