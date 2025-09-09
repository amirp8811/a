#!/usr/bin/env python3
"""
Simple CSS builder that combines Tailwind utilities with our custom styles.
This replaces the CDN approach for production.
"""

import os
import subprocess
import sys

def build_css():
    """Build production CSS using Tailwind CLI."""
    try:
        # Try to run tailwindcss with npm
        result = subprocess.run([
            'npm', 'run', 'build-css'
        ], capture_output=True, text=True, check=True)
        print("✅ CSS built successfully with npm script")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ npm build failed: {e}")
        # Try direct npx as fallback
        try:
            result = subprocess.run([
                'npx', 'tailwindcss', 
                '-i', './src/input.css',
                '-o', './anomidate_web/static/styles.css',
                '--minify'
            ], capture_output=True, text=True, check=True)
            print("✅ CSS built successfully with npx fallback")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e2:
            print(f"❌ npx fallback also failed: {e2}")
            return False

def create_fallback_css():
    """Create a fallback CSS file with essential styles."""
    css_content = """
/* Essential Tailwind utilities + custom styles */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { box-sizing: border-box; }
body { margin: 0; font-family: 'Inter', system-ui, -apple-system, sans-serif; }

/* Custom theme styles */
.theme { background: #0f1115; color: #e6e6e6; min-height: 100vh; }
.page { max-width: 1100px; margin: 0 auto; padding: 2rem 1.25rem; position: relative; z-index: 1; }
.site-glass { width: 100%; margin: 0 auto; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); box-shadow: 0 10px 30px rgba(0,0,0,0.25); backdrop-filter: blur(12px); padding: 2rem; border-radius: 22px; }

/* Buttons */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 0.6rem; padding: 0.8rem 1.1rem; background: #ec4899; color: #fff; border-radius: 999px; text-decoration: none; border: 0; transition: transform .12s ease, box-shadow .12s ease, background .12s ease; box-shadow: 0 8px 24px rgba(236,72,153,0.25); cursor: pointer; }
.btn:hover { transform: translateY(-1px); box-shadow: 0 12px 32px rgba(236,72,153,0.35); background: #f472b6; }
.btn.ghost { background: transparent; border: 1px solid #2a376a; color: #cfd6ff; }
.btn.outline { background: transparent; border: 1px solid #5865F2; color: #d7dcff; }

/* Cards */
.card { background: linear-gradient(180deg, rgba(19,23,34,0.74), rgba(13,17,26,0.74)); border: 1px solid #23273a; border-radius: 16px; padding: 1.25rem; backdrop-filter: blur(10px); box-shadow: 0 10px 30px rgba(0,0,0,0.25); }
.glass-card { background: rgba(255,255,255,0.12); backdrop-filter: blur(16px); box-shadow: 0 10px 30px rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.2); border-radius: 22px; }

/* Forms */
input, select, textarea { font: inherit; width: 100%; padding: 0.95rem 1.1rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.06); color: #ffffff; transition: border-color .12s ease, box-shadow .12s ease, background .12s ease; }
input::placeholder, textarea::placeholder { color: #fbcfe8; opacity: 0.75; }
input:focus, select:focus, textarea:focus { outline: none; border-color: #ec4899; box-shadow: 0 0 0 3px rgba(236,72,153,0.18); background: rgba(255,255,255,0.12); }

/* Auth styles */
.auth-wrap { display: flex; justify-content: center; align-items: center; padding: 2.5rem 1rem; }
.auth-card { width: 100%; max-width: 520px; background: linear-gradient(180deg, rgba(18,23,40,0.9), rgba(14,18,31,0.9)); border: 1px solid #23273a; border-radius: 18px; padding: 1.5rem; box-shadow: 0 20px 50px rgba(0,0,0,0.35); backdrop-filter: blur(6px); }
.auth-card h2 { margin: 0 0 0.35rem; }
.form { display: flex; flex-direction: column; gap: 1rem; max-width: 520px; }
.form label { display: flex; flex-direction: column; gap: 0.35rem; }
.link-cta { color: #cfd6ff; text-decoration: none; padding: 0.35rem 0.5rem; margin-left: 0.35rem; border-radius: 10px; border: 1px solid transparent; transition: transform .12s ease, background .12s ease, border-color .12s ease; }
.link-cta:hover { background: rgba(88,101,242,0.12); border-color: #2e3a70; transform: translateY(-1px); }
.auth-switch { display: flex; gap: 0.35rem; align-items: center; margin-top: 0.9rem; }

/* Dashboard */
.dash-hero { display: flex; align-items: center; justify-content: space-between; gap: 1rem; background: radial-gradient(900px 420px at 10% -10%, rgba(88,101,242,0.18), transparent), linear-gradient(180deg, #151823, #0f1115); border: 1px solid #23273a; border-radius: 18px; padding: 1.25rem 1.35rem; margin-bottom: 1rem; }
.dash-hero .title { font-size: 1.4rem; font-weight: 800; margin: 0; }
.dash-hero .subtitle { color: #b8bfd1; }
.stat-grid { display: grid; gap: 1rem; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: 1rem; }
.stat { background: linear-gradient(180deg, #121728, #101521); border: 1px solid #23273a; border-radius: 14px; padding: 0.9rem; }
.stat .label { color: #9aa3b2; font-size: 0.85rem; }
.stat .value { font-size: 1.4rem; font-weight: 800; }

/* Utility classes */
.muted { color: #9aa3b2; }
.text-center { text-align: center; }
.mb-6 { margin-bottom: 1.5rem; }
.mt-6 { margin-top: 1.5rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.gap-3 { gap: 0.75rem; }
.w-full { width: 100%; }
.max-w-md { max-width: 28rem; }
.rounded-2xl { border-radius: 1rem; }
.p-8 { padding: 2rem; }
.text-white { color: #ffffff; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
.font-bold { font-weight: 700; }
.block { display: block; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-white\/80 { color: rgba(255, 255, 255, 0.8); }
.mt-1 { margin-top: 0.25rem; }
.rounded-lg { border-radius: 0.5rem; }
.border-0 { border-width: 0; }
.bg-white { background-color: #ffffff; }
.text-gray-900 { color: #1f2937; }
.placeholder-gray-400::placeholder { color: #9ca3af; }
.shadow-sm { box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }
.focus\:ring-2:focus { box-shadow: 0 0 0 2px var(--tw-ring-color); }
.focus\:ring-indigo-500:focus { --tw-ring-color: #6366f1; }
.inline-flex { display: inline-flex; }
.justify-between { justify-content: space-between; }
.hover\:bg-indigo-500:hover { background-color: #6366f1; }
.focus\:outline-none:focus { outline: 2px solid transparent; outline-offset: 2px; }
.focus\:ring-white\/30:focus { --tw-ring-color: rgba(255, 255, 255, 0.3); }
.transition { transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }
.min-h-\[90vh\] { min-height: 90vh; }
.px-4 { padding-left: 1rem; padding-right: 1rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
.mb-3 { margin-bottom: 0.75rem; }
.w-12 { width: 3rem; }
.h-12 { height: 3rem; }
.rounded-xl { border-radius: 0.75rem; }
.bg-white\/20 { background-color: rgba(255, 255, 255, 0.2); }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.underline { text-decoration-line: underline; }
.decoration-white\\/40 { text-decoration-color: rgba(255, 255, 255, 0.4); }
.hover\\:decoration-white:hover { text-decoration-color: #ffffff; }
"""
    
    with open('./anomidate_web/static/styles.css', 'w', encoding='utf-8') as f:
        f.write(css_content.strip())
    print("✅ Created fallback CSS file")
    return True

if __name__ == "__main__":
    print("Building CSS for production...")
    if not build_css():
        print("Falling back to custom CSS...")
        create_fallback_css()
    print("CSS build complete!")
