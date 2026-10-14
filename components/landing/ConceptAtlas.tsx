'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, ArrowRight, ExternalLink, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';

interface ConceptEntry {
  id: string;
  title: string;
  category: 'Fundamentals' | 'Computing' | 'Algorithms' | 'Physics';
  symbol: string;
  tagline: string;
  formula: string;
  description: string;
  analogy: string;
  application: string;
  actionUrl: string;
  actionText: string;
  imageUrl?: string;
}

const ATLAS_ENTRIES: ConceptEntry[] = [
  {
    id: 'superposition',
    title: 'Superposition',
    category: 'Fundamentals',
    symbol: '|ψ⟩ = α|0⟩ + β|1⟩',
    tagline: 'Existing in a linear combination of physical states until measured.',
    formula: '|ψ⟩ = α|0⟩ + β|1⟩  where  |α|² + |β|² = 1',
    description:
      'In classical mechanics, a bit is strictly 0 or 1. In quantum mechanics, a system exists in a continuum of potential outcomes until measurement causes wavefunction collapse.',
    analogy:
      'Like a spinning coin: while rotating on a table, it is simultaneously a blend of heads and tails. Once caught, it collapses into a definite side.',
    application:
      'Quantum parallelism: evaluating massive solution spaces simultaneously in Shor’s and Grover’s algorithms.',
    actionUrl: '/simulate',
    actionText: 'Inspect on Bloch Sphere',
  },
  {
    id: 'entanglement',
    title: 'Quantum Entanglement',
    category: 'Computing',
    symbol: '|Φ⁺⟩ = (|00⟩+|11⟩)/√2',
    tagline: 'Non-local correlation between particles across arbitrary spatial distances.',
    formula: '|Φ⁺⟩ = (|00⟩ + |11⟩) / √2',
    description:
      'Two or more quantum particles become intertwined such that the quantum state of each particle cannot be described independently of the others, regardless of distance.',
    analogy:
      'Like a pair of magic shoes in two sealed boxes sent to opposite sides of the universe. The instant you open one and see a left shoe, you know the other box contains the right shoe.',
    application:
      'Quantum teleportation, superdense coding, and Bell-state cryptographic key distribution (BB84).',
    actionUrl: '/circuit',
    actionText: 'Build Bell State Circuit',
  },
  {
    id: 'bloch-sphere',
    title: 'The Bloch Sphere',
    category: 'Computing',
    symbol: 'S² Geodesic',
    tagline: 'A geometric representation of the pure state space of a two-level quantum system.',
    formula: '|ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩',
    description:
      'Points on the surface of the unit sphere correspond to pure qubit states. North and south poles represent |0⟩ and |1⟩, while the equator represents equal superpositions.',
    analogy:
      'A globe where the North Pole is 0 and South Pole is 1. A single quantum state can point anywhere—like Paris, Tokyo, or Quito.',
    application:
      'Visualizing single-qubit quantum logic gates (Pauli-X, Y, Z, Hadamard, Phase rotations).',
    actionUrl: '/simulate',
    actionText: 'Open 3D Bloch Sphere',
    imageUrl:
      'https://imgs.search.brave.com/esCzNItS7EAyOz-Z_Qzhq4pvLhp-37GxRSFRJKQUA80/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9xdXRp/cC5vcmcvZG9jcy80/LjAuMi9pbWFnZXMv/YmxvY2gzZCtkYXRh/LnBuZw',
  },
  {
    id: 'tunneling',
    title: 'Quantum Tunneling',
    category: 'Physics',
    symbol: 'T ≈ e^(-2κL)',
    tagline: 'Particles passing through energy barriers they cannot classically cross.',
    formula: 'T ≈ exp(-2L √(2m(V₀ - E)) / ℏ)',
    description:
      'Because matter exhibits wave-like characteristics, the wave function has a non-zero probability amplitude on the other side of an energetic barrier.',
    analogy:
      'Rolling a tennis ball against a brick wall. Classically it bounces back; quantum mechanically, the ball occasionally appears on the other side without breaking the wall.',
    application:
      'Scanning Tunneling Microscopes (STM), alpha radioactive decay, flash memory, and nuclear fusion in stars.',
    actionUrl: '/learn',
    actionText: 'Study in Quantum Module',
    imageUrl:
      'https://imgs.search.brave.com/hKrjq2IohMEQZmrtsxuDDNqKMfQF0iiw4X1d21awyZ8/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMubmV3YXRsYXMu/Y29tL2RpbXM0L2Rl/ZmF1bHQvNmYzZDU0/OC8yMTQ3NDgzNjQ3/L3N0cmlwL3RydWUv/Y3JvcC84MDB4NDQx/KzArMC9yZXNpemUv/ODAweDQ0MSEvZm9y/bWF0L3dlYnAvcXVh/bGl0eS85MC8_dXJs/PWh0dHBzOi8vbmV3/YXRsYXMtYnJpZ2h0/c3BvdC5zMy5hbWF6/b25hd3MuY29tL2Fy/Y2hpdmUvcXVhbnR1/bS10dW5uZWxsaW5n/LTQuanBlZw',
  },
  {
    id: 'grover',
    title: "Grover's Search Algorithm",
    category: 'Algorithms',
    symbol: 'O(√N) Speedup',
    tagline: 'Quadratic quantum acceleration for searching unstructured databases.',
    formula: 'R ≈ (π/4) · √N iterations',
    description:
      'Grover’s algorithm uses amplitude amplification to invert and amplify the probability amplitude of the marked target state relative to other states.',
    analogy:
      'Finding a needle in a haystack of 1,000,000 items: classical search takes 500,000 tries on average; Grover’s algorithm succeeds in only ~1,000 quantum queries.',
    application:
      'Database querying, collision attacks against cryptographic hash functions, optimization problems.',
    actionUrl: '/circuit',
    actionText: 'Run Grover Circuit',
    imageUrl:
      'https://imgs.search.brave.com/oYhVXR--fOhgXnSTa1EOHBeRa30Wkt2CyxIvkqG2wsM/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9xdWFu/dHVtLmNsb3VkLmli/bS5jb20vbGVhcm5p/bmcvaW1hZ2VzL21v/ZHVsZXMvY29tcHV0/ZXItc2NpZW5jZS9n/cm92ZXJzL2dyb3Zl/ci1vcmFjbGUtcXVl/c3Rpb24uYXZpZj9k/cGw9MC0xLTE1NjQt/NzczY2Y0NmNhYmU4'
  },
  {
    id: 'shor',
    title: "Shor's Factoring Algorithm",
    category: 'Algorithms',
    symbol: 'O((log N)³)',
    tagline: 'Polynomial-time prime factorization threatening classical RSA cryptography.',
    formula: 'a^r ≡ 1 (mod N) via Quantum Fourier Transform',
    description:
      'Shor’s algorithm reduces the problem of integer prime factorization to finding the period of a modular exponential function via the Quantum Fourier Transform (QFT).',
    analogy:
      'Using constructive quantum wave interference to find the secret rhythm or cycle of an astronomical clock in seconds instead of millennia.',
    application:
      'Post-quantum cryptography (PQC), quantum key distribution, integer factorization analysis.',
    actionUrl: '/learn',
    actionText: 'Explore Shor Roadmap',
    imageUrl:
      'https://imgs.search.brave.com/uKC4Px_LxThx6BpdOUTXxjgPd58HtV13N79yEgOrwjw/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jb2xv/cnRva2Vucy5jb20v/d3AtY29udGVudC91/cGxvYWRzL2ltYWdl/LTEwNy53ZWJw'
  },
  {
    id: 'qubits-gates',
    title: 'Quantum Logic Gates',
    category: 'Computing',
    symbol: 'U · U† = I',
    tagline: 'Unitary transformations rotating state vectors on the complex Hilbert space.',
    formula: 'H = 1/√2 [[1, 1], [1, -1]]',
    description:
      'Unlike irreversible classical Boolean gates (AND, OR), quantum gates are reversible unitary matrices preserving the norm of probability vectors.',
    analogy:
      'Rotating a physical compass in 3D: you can always rotate it backward to exactly recover the original position.',
    application:
      'Designing arbitrary universal quantum computing circuits in Qiskit, Cirq, and Pennylane.',
    actionUrl: '/circuit',
    actionText: 'Drag-and-Drop Gate Editor',
    imageUrl:
      'https://imgs.search.brave.com/lZnzDzjH2FTXEFhWh26PjolxU0uK3zGzMNRBJr-w0-o/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jZG4t/aW1hZ2VzLTEubWVk/aXVtLmNvbS9tYXgv/ODAwLzEqQXZCcWhj/N1ZCOE1ZNHNTX2lO/WUhtQS5qcGVn'
  },
  {
    id: 'decoherence',
    title: 'Quantum Decoherence',
    category: 'Physics',
    symbol: 'T₁, T₂ Relaxation',
    tagline: 'Loss of quantum coherence due to environmental noise and entanglement.',
    formula: 'ρ_ij(t) = ρ_ij(0) · exp(-t / T₂)',
    description:
      'The transition of a pure quantum state into a classical statistical mixture as energy and phase leak into ambient thermal fluctuations.',
    analogy:
      'A delicate musical note struck inside a bustling marketplace—the acoustics gradually blend into environmental noise.',
    application:
      'Quantum error correction (QEC), surface codes, and ultra-cold dilution refrigerators (15 mK).',
    actionUrl: '/ai-tutor',
    actionText: 'Ask AI Tutor on Decoherence',
    imageUrl:
      'https://imgs.search.brave.com/KyT-DHYmnMK-LT4B-Ud3HaYuY_f4N2_7Sd1lp8w3JaY/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9zZWxm/YXdhcmVwYXR0ZXJu/cy5jb20vd3AtY29u/dGVudC91cGxvYWRz/LzIwMjAvMTIvMTAy/NHB4LWRvdWJsZS1z/bGl0LnN2Z18ucG5n'
  },
];

export default function ConceptAtlas() {
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeModalEntry, setActiveModalEntry] = useState<ConceptEntry | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [hoveredEntryId, setHoveredEntryId] = useState<string | null>(null);

  const categories = ['All', 'Fundamentals', 'Computing', 'Algorithms', 'Physics'];

  const filteredEntries = ATLAS_ENTRIES.filter((entry) => {
    const matchesCat = selectedCategory === 'All' || entry.category === selectedCategory;
    const matchesSearch =
      entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.tagline.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  const VISIBLE = 4;
  const STEP = 2;
  const maxIndex = Math.max(0, filteredEntries.length - VISIBLE);
  const nextSlide = () => setCurrentIndex((prev) => Math.min(prev + STEP, maxIndex));
  const prevSlide = () => setCurrentIndex((prev) => Math.max(prev - STEP, 0));

  return (
    <div style={{ position: 'relative' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 16,
          marginBottom: 36,
        }}
      >
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {categories.map((cat) => {
            const isActive = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => { setSelectedCategory(cat); setCurrentIndex(0); }}
                style={{
                  fontFamily: "'Exo 2', sans-serif",
                  padding: '8px 18px',
                  borderRadius: 999,
                  fontSize: 14,
                  fontWeight: 600,
                  border: isActive ? '1.5px solid #ED6A5A' : '1px solid #E2E6DF',
                  background: isActive ? '#ED6A5A' : '#FFFFFF',
                  color: isActive ? '#FFFFFF' : '#5A6578',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: isActive ? '0 4px 12px rgba(237, 106, 90, 0.25)' : 'none',
                }}
              >
                {cat}
              </button>
            );
          })}
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: '#FFFFFF',
            border: '1.5px solid #E2E6DF',
            borderRadius: 999,
            padding: '8px 18px',
            width: '100%',
            maxWidth: 300,
            boxShadow: '0 2px 8px rgba(34, 37, 42, 0.04)',
          }}
        >
          <Search size={16} color="#5A6578" />
          <input
            type="text"
            placeholder="Search entries..."
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setCurrentIndex(0); }}
            style={{
              border: 'none',
              outline: 'none',
              fontSize: 14,
              fontFamily: "'Exo 2', sans-serif",
              color: '#22252A',
              width: '100%',
              background: 'transparent',
            }}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
            >
              <X size={14} color="#5A6578" />
            </button>
          )}
        </div>
      </div>

      {/* Slider viewport */}
      <div style={{ position: 'relative', overflow: 'hidden', padding: '20px 0' }}>
        {/* Track — each card is 25% wide (gap handled via padding) */}
        <div
          style={{
            height: '360px',
            display: 'flex',
            justifyContent: 'center',
            transition: 'transform 0.45s cubic-bezier(0.4, 0, 0.2, 1)',
            transform: `translateX(calc(-${currentIndex * 25}%))`,
          }}
        >
          {filteredEntries.map((entry) => (
            <div
              key={entry.id}
              style={{
                minWidth: 'calc(25% - 12px)',
                flex: '0 0 calc(25% - 12px)',
                margin: '0 6px',
              }}
            >
              <div
                onClick={() => setActiveModalEntry(entry)}
                onMouseEnter={() => setHoveredEntryId(entry.id)}
                onMouseLeave={() => setHoveredEntryId(null)}
                className="atlas-card"
                style={{
                  position: 'relative',
                  cursor: 'pointer',
                  width: '280px',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  overflow: 'hidden',
                  borderRadius: 0,
                }}
              >


                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    width: '100%',
                    height: '100%',
                  }}
                >
                  <img
                    src={entry.imageUrl ?? 'https://www.shutterstock.com/image-vector/classical-vs-quantum-bit-visualizing-260nw-2621511891.jpg'}
                    alt=""
                    aria-hidden="true"
                    style={{
                      maxWidth: '100%',
                      maxHeight: '100%',
                      objectFit: 'contain',
                    }}
                  />
                </div>
                <div
                  style={{
                    marginTop: 'auto',
                    border: 'none',
                    position: 'relative',
                    padding: '5px 5px',
                    flex: '0 0 auto',
                    zIndex: 1,
                    backdropFilter: 'blur(5px)',
                    backgroundColor: hoveredEntryId === entry.id ? '#F59E0B' : 'transparent',
                    transition: 'all 0.5s ease',
                  }}
                >
                  <h3 style={{ fontSize: 16, padding: '5px 3px', margin: 'auto 0 0' }}>{entry.title}</h3>
                  <p style={{ color: '#6b6e74', fontSize: 12.5, padding: '0 3px 3px 3px' }}>{entry.tagline}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Prev button */}
        <button
          onClick={prevSlide}
          disabled={currentIndex === 0}
          style={{
            position: 'absolute',
            left: -18,
            top: '50%',
            transform: 'translateY(-50%)',
            zIndex: 10,
            background: currentIndex === 0 ? '#F5F5F3' : '#FFFFFF',
            border: '1.5px solid #E2E6DF',
            borderRadius: '50%',
            width: 40,
            height: 40,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: currentIndex === 0 ? 'not-allowed' : 'pointer',
            opacity: currentIndex === 0 ? 0.45 : 1,
            boxShadow: '0 2px 8px rgba(34,37,42,0.1)',
            transition: 'all 0.2s',
          }}
        >
          <ChevronLeft size={18} />
        </button>

        {/* Next button */}
        <button
          onClick={nextSlide}
          disabled={currentIndex >= maxIndex}
          style={{
            position: 'absolute',
            right: -18,
            top: '50%',
            transform: 'translateY(-50%)',
            zIndex: 10,
            background: currentIndex >= maxIndex ? '#F5F5F3' : '#FFFFFF',
            border: '1.5px solid #E2E6DF',
            borderRadius: '50%',
            width: 40,
            height: 40,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: currentIndex >= maxIndex ? 'not-allowed' : 'pointer',
            opacity: currentIndex >= maxIndex ? 0.45 : 1,
            boxShadow: '0 2px 8px rgba(34,37,42,0.1)',
            transition: 'all 0.2s',
          }}
        >
          <ChevronRight size={18} />
        </button>
      </div>

      {/* Dot indicators — one dot per possible stop (step of 2) */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 16 }}>
        {Array.from({ length: maxIndex + 1 }, (_, i) => i).filter((i) => i % STEP === 0 || i === maxIndex).map((stopIndex) => (
          <div
            key={stopIndex}
            onClick={() => setCurrentIndex(stopIndex)}
            style={{
              width: currentIndex === stopIndex ? 20 : 8,
              height: 8,
              borderRadius: 4,
              background: currentIndex === stopIndex ? '#ED6A5A' : '#E2E6DF',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
          />
        ))}
      </div>

      <AnimatePresence>
        {activeModalEntry && (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 100,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 20,
              background: 'rgba(34, 37, 42, 0.55)',
              backdropFilter: 'blur(8px)',
            }}
            onClick={() => setActiveModalEntry(null)}
          >
            <motion.div
              initial={{ scale: 0.94, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.94, opacity: 0 }}
              transition={{ duration: 0.25 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: '#FFFFFF',
                borderRadius: 24,
                width: '100%',
                maxWidth: 620,
                maxHeight: '90vh',
                overflowY: 'auto',
                padding: '36px 32px',
                position: 'relative',
                boxShadow: '0 24px 64px rgba(34, 37, 42, 0.25)',
                border: '1px solid #E2E6DF',
              }}
            >
              <button
                onClick={() => setActiveModalEntry(null)}
                style={{
                  position: 'absolute',
                  top: 20,
                  right: 20,
                  background: '#FAFAF8',
                  border: '1px solid #E2E6DF',
                  borderRadius: '50%',
                  width: 36,
                  height: 36,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  color: '#22252A',
                }}
              >
                <X size={18} />
              </button>
              <div style={{ marginBottom: 12 }}>
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: '#ED6A5A',
                    background: '#FDECE9',
                    padding: '4px 12px',
                    borderRadius: 999,
                  }}
                >
                  {activeModalEntry.category} Entry
                </span>
              </div>
              <h2
                style={{
                  fontFamily: "'Exo 2', sans-serif",
                  fontWeight: 800,
                  fontSize: 28,
                  color: '#22252A',
                  marginBottom: 8,
                }}
              >
                {activeModalEntry.title}
              </h2>
              <p
                style={{
                  fontSize: 16,
                  color: '#5A6578',
                  fontStyle: 'italic',
                  marginBottom: 20,
                  fontFamily: "'Lora', serif",
                }}
              >
                &ldquo;{activeModalEntry.tagline}&rdquo;
              </p>
              <div
                style={{
                  background: '#FAFAF8',
                  border: '1.5px solid #E2E6DF',
                  borderRadius: 14,
                  padding: '14px 18px',
                  marginBottom: 24,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                }}
              >
                <span style={{ fontSize: 18 }}>📐</span>
                <span
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 14,
                    color: '#22252A',
                    fontWeight: 600,
                  }}
                >
                  {activeModalEntry.formula}
                </span>
              </div>
              <div style={{ marginBottom: 20 }}>
                <h4 style={{ fontSize: 13, textTransform: 'uppercase', color: '#5A6578', fontWeight: 700, marginBottom: 6 }}>
                  Scientific Description
                </h4>
                <p style={{ color: '#22252A', fontSize: 15, lineHeight: 1.7 }}>
                  {activeModalEntry.description}
                </p>
              </div>
              <div
                style={{
                  background: '#E6EBE0',
                  borderRadius: 14,
                  padding: '16px 20px',
                  marginBottom: 20,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 700, fontSize: 13, color: '#22252A', marginBottom: 4 }}>
                  <Sparkles size={16} color="#ED6A5A" /> Intuitive Analogy
                </div>
                <p style={{ fontSize: 14, color: '#3A3F47', lineHeight: 1.6, margin: 0 }}>
                  {activeModalEntry.analogy}
                </p>
              </div>
              <div style={{ marginBottom: 28 }}>
                <h4 style={{ fontSize: 13, textTransform: 'uppercase', color: '#5A6578', fontWeight: 700, marginBottom: 6 }}>
                  Real-World Application
                </h4>
                <p style={{ color: '#22252A', fontSize: 14, lineHeight: 1.6 }}>
                  {activeModalEntry.application}
                </p>
              </div>
              <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                <Link
                  href={activeModalEntry.actionUrl}
                  onClick={() => setActiveModalEntry(null)}
                  className="btn-atlas-coral"
                  style={{ textDecoration: 'none' }}
                >
                  {activeModalEntry.actionText} <ExternalLink size={15} />
                </Link>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
