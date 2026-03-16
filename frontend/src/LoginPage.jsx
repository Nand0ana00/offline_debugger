import React, { useState } from 'react'
import { motion as Motion } from 'framer-motion'
import { Zap, User, Lock, ArrowRight } from 'lucide-react'

export default function LoginPage({ onLogin }) {
    const [isRegister, setIsRegister] = useState(false)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [displayName, setDisplayName] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            if (!username.trim() || !password.trim()) {
                throw new Error('Please enter both username and password.')
            }

            // Mock success for demo
            const mockUser = {
                username: username.trim(),
                display_name: isRegister ? (displayName || username.trim()) : username.trim()
            }

            onLogin(mockUser)
        } catch (err) {
            setError(err.message)
            setLoading(false)
        }
    }

    return (
        <div className="login-page" style={{ position: 'fixed', inset: 0, zIndex: 9999 }}>
            <div className="login-particles">
                {[...Array(3)].map((_, i) => (
                    <div key={i} className={`login-particle particle-${i}`} />
                ))}
            </div>

            <Motion.div
                className="login-container"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
                <div className="login-logo">
                    <div className="login-logo-icon">
                        <Zap size={32} color="white" fill="white" />
                    </div>
                    <div className="login-logo-text">
                        <span className="login-brand-top">OFFLINE</span>
                        <span className="login-brand-bottom">AI DEBUGGER</span>
                    </div>
                </div>

                <p className="login-subtitle">
                    {isRegister ? 'Join the next generation of debugging' : 'Initialize secure session'}
                </p>

                <form onSubmit={handleSubmit} className="login-form">
                    {isRegister && (
                        <div className="login-input-group">
                            <User size={18} className="login-input-icon" />
                            <input
                                type="text"
                                placeholder="Full Name"
                                value={displayName}
                                onChange={e => setDisplayName(e.target.value)}
                                className="login-input"
                            />
                        </div>
                    )}

                    <div className="login-input-group">
                        <User size={18} className="login-input-icon" />
                        <input
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            className="login-input"
                            required
                        />
                    </div>

                    <div className="login-input-group">
                        <Lock size={18} className="login-input-icon" />
                        <input
                            type="password"
                            placeholder="Auth Key"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            className="login-input"
                            required
                        />
                    </div>

                    {error && <div className="login-error" style={{ color: '#f87171', fontSize: '0.875rem', marginTop: '0.5rem', textAlign: 'center' }}>{error}</div>}

                    <button type="submit" className="login-submit" disabled={loading} style={{ marginTop: '1.5rem' }}>
                        {loading ? 'Authenticating...' : (isRegister ? 'Create Profile' : 'Access Terminal')}
                        {!loading && <ArrowRight size={18} />}
                    </button>
                </form>

                <div className="login-toggle">
                    <span className="login-toggle-text">
                        {isRegister ? 'Already registered?' : 'New developer?'}
                    </span>
                    <button
                        type="button"
                        className="login-toggle-btn"
                        onClick={() => { setIsRegister(!isRegister); setError('') }}
                    >
                        {isRegister ? 'Sign In' : 'Register Access'}
                    </button>
                </div>

                <div className="login-footer">
                    100% OFFLINE NEURAL PIPELINE
                </div>
            </Motion.div>
        </div>
    )
}
