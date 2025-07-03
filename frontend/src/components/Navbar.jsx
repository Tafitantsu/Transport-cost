import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '@styles/Navbar.css';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false); // État pour le menu mobile

  const toggleMenu = () => setIsOpen(!isOpen); // Fonction pour basculer le menu

  return (
    <nav className="navbar">
      <div className="navbar-container">
        
        <button
          className="navbar-toggle"
          onClick={toggleMenu}
          aria-label="Toggle navigation"
          aria-expanded={isOpen}
        >
          <span className="hamburger-icon">☰</span>
        </button>
        <ul className={`navbar-links ${isOpen ? 'active' : ''}`}>
        <li>
            <Link to="/" onClick={() => setIsOpen(false)}>
              🏠 Accueil
            </Link>
          </li>
          <li>
            <Link to="/create" onClick={() => setIsOpen(false)}>
              ➕ Créer
            </Link>
          </li>
          <li>
            <Link to="/list" onClick={() => setIsOpen(false)}>
              📋 Lister les tâches
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;