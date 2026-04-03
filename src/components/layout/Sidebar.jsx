import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, FileText, LayoutDashboard, BarChart2, Settings, Box } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const navItems = [
    { path: '/chat', name: 'Chat', icon: MessageSquare },
    { path: '/documents', name: 'Documents', icon: FileText },
    { path: '/dashboard', name: 'Dashboard', icon: LayoutDashboard },
    { path: '/reports', name: 'Reports', icon: BarChart2 },
    { path: '/settings', name: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <Box fill="currentColor" />
        </div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}
          >
            <item.icon className="sidebar-item-icon" size={24} />
            <span className="sidebar-item-text">{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
