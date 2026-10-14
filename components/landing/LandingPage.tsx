'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Compass,
  Cpu,
  Sparkles,
  Layers,
  Gamepad2,
  MessageSquare,
  Trophy,
  CheckCircle2,
  Atom,
  Eye,
  Sliders,
  Share2,
  Mail,
  HelpCircle,
} from 'lucide-react';

import AtlasLogo from './AtlasLogo';
import AtlasNav from '../shared/AtlasNav';
import QuantumBackground3D from './QuantumBackground3D';
import InteractiveSimCard from './InteractiveSimCard';
import ConceptAtlas from './ConceptAtlas';
import Stickman from '../roadmap/Stickman';
import { TRACKS, RESOURCES, TOTAL_MILESTONES, TOTAL_RESOURCES } from '../roadmap/roadmapData';

export default function QuantumAtlasLandingPage() {
  const TESTIMONIALS = [
    {
      quote:
        'The interactive simulations and visual Bloch spheres in the Qurio Atlas finally made superposition and phase rotations click. It feels like an authentic scientific field guide.',
      name: 'Dr. VISHNU RAI',
      affiliation: 'Quantum Information Fellow, IISc',
      role: 'Researcher',
    },
    {
      quote:
        'The combination of a live drag-and-drop circuit editor with intuitive explanations and AI tutoring is second to none. We use it weekly in our quantum algorithms class.',
      name: 'Devanathan K.',
      affiliation: 'IIT Madras, CS Department',
      role: 'Student & Hackathon Finalist',
    },
    {
      quote:
        'Approachable, scientifically grounded, and visually breathtaking. It takes quantum physics from intimidating blackboard equations into an intuitive playground.',
      name: 'Sophia Lindqvist',
      affiliation: 'Nordic Quantum Network',
      role: 'Science Communicator',
    },
  ];

  return (
    <div
      style={{
        background: '#FAFAF8',
        color: '#22252A',
        minHeight: '100vh',
        fontFamily: "'Inter', sans-serif",
        position: 'relative',
        overflowX: 'hidden',
      }}
    >
      {/* ══════════════════════════════════════════════
          3D QUANTUM PHYSICS BACKGROUND ANIMATION
      ══════════════════════════════════════════════ */}
      <QuantumBackground3D />

      {/* ══════════════════════════════════════════════
          TOP NAVIGATION BAR (Quantum Atlas Style)
      ══════════════════════════════════════════════ */}
      <AtlasNav current="home" />

      {/* ══════════════════════════════════════════════
          CONTENT LAYERS (ON TOP OF 3D QUANTUM ENGINE)
      ══════════════════════════════════════════════ */}
      <div className="atlas-content-layer">
        {/* ── HERO SECTION ── */}
        <header
          style={{
            minHeight: '82vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '70px 28px 90px',
            position: 'relative',
          }}
        >
          <div
            style={{
              maxWidth: 1120,
              width: '100%',
              margin: '0 auto',
              display: 'grid',
              gridTemplateColumns: '1fr',
              alignItems: 'center',
            }}
          >
            {/* Signature Editorial Statement */}
            <motion.div
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.15 }}
            >
              {/* Badge */}
              {/* <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '6px 14px',
                  borderRadius: 999,
                  background: '#E6EBE0',
                  color: '#22252A',
                  fontSize: 13,
                  fontWeight: 600,
                  marginBottom: 24,
                  border: '1px solid rgba(34, 37, 42, 0.1)',
                }}
              >
              </div> */}

              {/* Main Headline with authentic Quantum Atlas phrasing & marker */}
              <h1
                style={{
                  fontFamily: "'Exo 2', sans-serif",
                  fontSize: '30px',
                  fontWeight: 500,
                  lineHeight: 1.25,
                  color: '#36373a',
                  letterSpacing: '-0.02em',
                  marginBottom: 20,
                }}
              >
                <span className="atlas-marker" style={{fontSize: 'clamp(3rem, 4vw, 4rem)',color:"black"}}>Quantum Computing</span> <br/>isn't science fiction—it's the next language of computation.
              </h1>

              <p
                style={{
                  fontFamily: "'Lora', serif",
                  fontSize: 'clamp(1.4rem, 2.2vw, 1.85rem)',
                  color: '#5A6578',
                  lineHeight: 1.4,
                  fontWeight: 300,
                  marginBottom: 32,
                }}
              >
               Where curiosity meets quantum intelligence.
              </p>

              {/* Approachable subtext */}
              <p
                style={{
                  fontSize: 16.5,
                  color: '#475569',
                  lineHeight: 1.7,
                  maxWidth: 640,
                  marginBottom: 36,
                }}
              >
                <span style={{fontWeight:'bold'}}>Qurio</span> is an immersive learning platform where quantum computing comes alive through interactive simulations, visual circuit design, intelligent guidance, and curated knowledge pathways. Learn by exploring—not memorizing.
              </p>

              {/* CTAs */}
              <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', alignItems: 'center' }}>
                <a href="#start" className="btn-atlas-coral">
                  Begin the Journey <ArrowRight size={16} />
                </a>


                <Link
                  href="/circuit"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    color: '#0081A7',
                    fontWeight: 600,
                    fontSize: 14.5,
                    textDecoration: 'none',
                    padding: '8px 12px',
                    marginLeft: 4,
                  }}
                >
                  <Cpu size={16} /> Try Circuit Studio →
                </Link>
              </div>
            </motion.div>
          </div>
        </header>

        {/* ══════════════════════════════════════════════
            MIDDLE SAGE RIBBON: THE 3 PILLARS (Quantum Atlas Fold)
        ══════════════════════════════════════════════ */}
        <section id="start" className="atlas-sage-panel" style={{ padding: '80px 28px', borderTop: '1px solid #D5DDD0', borderBottom: '1px solid #D5DDD0' }}>
          {/* Subtle wavy contour SVG header */}
          <div style={{ maxWidth: 1160, margin: '0 auto' }}>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 32,
              }}
            >
              {/* Pillar 1: Get Started */}
              <motion.div
                whileHover={{ y: -6 }}
                transition={{ duration: 0.25 }}
                className="atlas-card"
                style={{ padding: 32, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
              >
                <div
                  style={{
                    width: 72,
                    height: 72,
                    borderRadius: '50%',
                    background: '#FDECE9',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 20,
                  }}
                >
                  <Compass size={36} color="#ED6A5A" />
                </div>
                <h3 style={{ fontFamily: "'Exo 2', sans-serif", fontSize: 24, fontWeight: 600, color: '#22252A', marginBottom: 12 }}>
                  Roadmap 
                </h3>
                <p style={{ color: '#5A6578', fontSize: 15, lineHeight: 1.6, marginBottom: 24, flex: 1 }}>
                 Step into the quantum world—where particles behave beyond imagination.
                </p>
                <Link
                  href="/roadmap"
                  className="btn-atlas-coral"
                  style={{ width: '100%', justifyContent: 'center', fontSize: 14 }}
                >
                  Start Guided Path <ArrowRight size={14} />
                </Link>
              </motion.div>

              {/* Pillar 2: Poke Around / Atlas Entries */}
              <motion.div
                whileHover={{ y: -6 }}
                transition={{ duration: 0.25 }}
                className="atlas-card"
                style={{ padding: 32, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
              >
                <div
                  style={{
                    width: 72,
                    height: 72,
                    borderRadius: '50%',
                    background: '#E6F4F8',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 20,
                  }}
                >
                  <Gamepad2 size={34} color="#0081A7" />
                </div>
                <h3 style={{ fontFamily: "'Exo 2', sans-serif", fontSize: 24, fontWeight: 600, color: '#22252A', marginBottom: 12 }}>
                  Qurio Qubit
                </h3>
                <p style={{ color: '#5A6578', fontSize: 15, lineHeight: 1.6, marginBottom: 24, flex: 1 }}>
                  Six stickman games, one per Base Camp module. Prove the theory landed, and collect
                  bronze, silver and gold on the way up.
                </p>
                <Link
                  href="/qubit"
                  className="btn-atlas-ghost"
                  style={{ width: '100%', justifyContent: 'center', fontSize: 14, borderColor: '#0081A7', color: '#0081A7' }}
                >
                  Play the games <ArrowRight size={14} />
                </Link>
              </motion.div>

              {/* Pillar 3: Interactive Labs & Simulation */}
              <motion.div
                whileHover={{ y: -6 }}
                transition={{ duration: 0.25 }}
                className="atlas-card"
                style={{ padding: 32, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
              >
                <div
                  style={{
                    width: 72,
                    height: 72,
                    borderRadius: '50%',
                    background: '#FEF3C7',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 20,
                  }}
                >
                  <Cpu size={36} color="#D97706" />
                </div>
                <h3 style={{ fontFamily: "'Exo 2', sans-serif", fontSize: 24, fontWeight: 600, color: '#22252A', marginBottom: 12 }}>
                  Circuit Realm
                </h3>
                <p style={{ color: '#5A6578', fontSize: 15, lineHeight: 1.6, marginBottom: 24, flex: 1 }}>
                  Drag-and-drop quantum gate circuits, execute algorithms with real-time Qiskit code generation, and test
                  probabilities.
                </p>
                <Link
                  href="/circuit"
                  className="btn-atlas-ghost"
                  style={{ width: '100%', justifyContent: 'center', fontSize: 14, borderColor: '#D97706', color: '#D97706' }}
                >
                  Open Circuit Studio <ArrowRight size={14} />
                </Link>
              </motion.div>
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════
            SECTION 1: INTERACTIVES (Quantum Atlas Split Layout)
        ══════════════════════════════════════════════ */}
        <section id="interactives" style={{ padding: '110px 28px', background: 'transparent' }}>
          <div
            style={{
              maxWidth: 1180,
              margin: '0 auto',
              display: 'grid',
              gridTemplateColumns: '1fr 1.25fr',
              gap: 60,
              alignItems: 'center',
            }}
          >
            {/* Left Editorial Text */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2
                style={{
                  fontFamily: "'Exo 2', sans-serif",
                  fontSize: 'clamp(2.4rem, 4vw, 3.2rem)',
                  fontWeight: 600,
                  color: '#22252A',
                  marginBottom: 20,
                  letterSpacing: '-0.02em',
                }}
              >
                <span className="atlas-marker">Interactives</span>
              </h2>

              <p
                style={{
                  fontFamily: "'Lora', serif",
                  fontSize: 20,
                  color: '#3A3F47',
                  lineHeight: 1.6,
                  marginBottom: 24,
                }}
              >
                We think quantum concepts are easier to understand if you can play around with them.
              </p>

              <p style={{ color: '#5A6578', fontSize: 15.5, lineHeight: 1.7, marginBottom: 32 }}>
                Textbooks often trap students in differential equations and high-dimensional Hilbert spaces. With our
                interactive sandboxes, you can manipulate quantum wave interference, adjust slit widths, rotate Bloch
                vectors, and observe probabilistic measurement collapse in real time.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <CheckCircle2 size={18} color="#ED6A5A" />
                  <span style={{ fontSize: 14.5, color: '#22252A', fontWeight: 500 }}>
                    Dual-slit probability wave interference simulator
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <CheckCircle2 size={18} color="#ED6A5A" />
                  <span style={{ fontSize: 14.5, color: '#22252A', fontWeight: 500 }}>
                    3D Bloch Sphere statevector precessions & unitary transformations
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <CheckCircle2 size={18} color="#ED6A5A" />
                  <span style={{ fontSize: 14.5, color: '#22252A', fontWeight: 500 }}>
                    Instant Python Qiskit code export for IBM Quantum execution
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Right Interactive Simulation Widget */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <InteractiveSimCard />
            </motion.div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════
            SECTION 2: ANIMATIONS & 3D QUANTUM SIMULATIONS
        ══════════════════════════════════════════════ */}
        <section style={{ padding: '110px 28px', background: 'rgba(230, 235, 224, 0.45)', borderTop: '1px solid #E2E6DF', borderBottom: '1px solid #E2E6DF' }}>
          <div
            style={{
              maxWidth: 1180,
              margin: '0 auto',
              display: 'grid',
              gridTemplateColumns: '1.2fr 1fr',
              gap: 60,
              alignItems: 'center',
            }}
          >
            {/* Left Graphic Showcase Card */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <div
                className="atlas-card"
                style={{
                  padding: 28,
                  background: '#FFFFFF',
                  border: '1.5px solid #E2E6DF',
                  boxShadow: '0 20px 48px rgba(34, 37, 42, 0.07)',
                }}
              >
                {/* Circuit and Gate Animation Showcase */}
                <div
                  style={{
                    background: '#FAFAF8',
                    border: '1px solid #E2E6DF',
                    borderRadius: 16,
                    padding: 24,
                    marginBottom: 20,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 18 }}>⚛️</span>
                      <span style={{ fontFamily: "'Exo 2', sans-serif", fontWeight: 700, fontSize: 15, color: '#22252A' }}>
                        Entangled Bell State Generator
                      </span>
                    </div>
                    <span
                      style={{
                        fontSize: 11,
                        background: '#FDECE9',
                        color: '#ED6A5A',
                        padding: '3px 8px',
                        borderRadius: 6,
                        fontWeight: 700,
                      }}
                    >
                      |Φ⁺⟩ STATE
                    </span>
                  </div>

                  {/* Wire lines */}
                  {[0, 1].map((q) => (
                    <div key={q} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
                      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: 13, color: '#0081A7', width: 34 }}>
                        |q{q}⟩
                      </span>
                      <div
                        style={{
                          flex: 1,
                          height: 2,
                          background: '#CBD5E1',
                          position: 'relative',
                          display: 'flex',
                          alignItems: 'center',
                        }}
                      >
                        {q === 0 && (
                          <>
                            <div
                              style={{
                                position: 'absolute',
                                left: '25%',
                                width: 36,
                                height: 36,
                                background: '#FFFFFF',
                                border: '2px solid #ED6A5A',
                                borderRadius: 8,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontWeight: 800,
                                fontSize: 13,
                                color: '#ED6A5A',
                                boxShadow: '0 4px 10px rgba(237, 106, 90, 0.2)',
                              }}
                            >
                              H
                            </div>
                            <div
                              style={{
                                position: 'absolute',
                                left: '60%',
                                width: 10,
                                height: 10,
                                background: '#0081A7',
                                borderRadius: '50%',
                              }}
                            />
                            {/* Vertical CNOT control line */}
                            <div
                              style={{
                                position: 'absolute',
                                left: 'calc(60% + 4px)',
                                top: 4,
                                width: 2,
                                height: 42,
                                background: '#0081A7',
                                zIndex: 1,
                              }}
                            />
                          </>
                        )}
                        {q === 1 && (
                          <div
                            style={{
                              position: 'absolute',

                              left: '60%',
                              width: 32,
                              height: 32,
                              background: '#FFFFFF',
                              border: '2px solid #0081A7',
                              borderRadius: '50%',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 800,
                              fontSize: 16,
                              color: '#0081A7',
                              transform: 'translate(-11px, -15px)',
                              zIndex: 2,
                              boxShadow: '0 4px 10px rgba(0, 129, 167, 0.2)',
                            }}
                          >

                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Measurement Outcome Box */}
                  <div
                    style={{
                      background: '#FFFFFF',
                      border: '1px solid #E2E6DF',
                      borderRadius: 10,
                      padding: '10px 14px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginTop: 20,
                    }}
                  >
                    <span style={{ fontSize: 12, color: '#5A6578', fontWeight: 600 }}>OUTCOME PROBABILITIES:</span>
                    <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, fontWeight: 700, color: '#22252A' }}>
                      |00⟩: 50.0% · |11⟩: 50.0%
                    </span>
                  </div>
                </div>

                {/* 3D Background Engine Callout */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: '#E6EBE0',
                    borderRadius: 12,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Atom size={18} color="#ED6A5A" />
                    <span style={{ fontSize: 13, fontWeight: 600, color: '#22252A' }}>
                      3D Engine Playing in Background
                    </span>
                  </div>
                  <span style={{ fontSize: 12, color: '#5A6578' }}>
                    Use the bottom-right HUD to change views ↘
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Right Editorial Text */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2
                style={{
                  fontFamily: "'Exo 2', sans-serif",
                  fontSize: 'clamp(2.4rem, 4vw, 3.2rem)',
                  fontWeight: 600,
                  color: '#22252A',
                  marginBottom: 20,
                  letterSpacing: '-0.02em',
                }}
              >
                <span className="atlas-marker">Animations</span>
              </h2>

              <p
                style={{
                  fontFamily: "'Lora', serif",
                  fontSize: 20,
                  color: '#3A3F47',
                  lineHeight: 1.6,
                  marginBottom: 24,
                }}
              >
                Graphics can help kindle your imagination and bring the quantum world to life.
              </p>

              <p style={{ color: '#5A6578', fontSize: 15.5, lineHeight: 1.7, marginBottom: 32 }}>
                Quantum mechanics deals with entities smaller than light itself—meaning no human eye can ever look directly
                at an electron orbital or a quantum spin vector. Through mathematical visualizations, three-dimensional
                renderings, and motion graphics, abstract quantum behaviors turn into vivid, graspable mental models.
              </p>

              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <Link href="/simulate" className="btn-atlas-coral">
                  Launch 3D Bloch Simulator <ArrowRight size={16} />
                </Link>
                <Link href="/ai-tutor" className="btn-atlas-ghost">
                  <MessageSquare size={16} /> Ask AI Tutor
                </Link>
              </div>
            </motion.div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════
            SECTION 3: THE CONCEPT ATLAS (ENTRIES CATALOG)
        ══════════════════════════════════════════════ */}
        <section id="entries" style={{ height: '850px', padding: '0 28px', background: '#FAFAF8', justifyContent: 'center', alignItems: 'center', display: 'flex' }}>
          <div style={{ maxWidth: 1180, margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: 54 }}>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '5px 14px',
                  borderRadius: 999,
                  background: '#E6EBE0',
                  fontSize: 13,
                  fontWeight: 600,
                  color: '#22252A',
                  marginBottom: 16,
                }}
              >
                📖 The Living Encyclopedia
              </div>

              <h2
                style={{
                  fontFamily: "'Exo 2', sans-serif",
                  fontSize: 'clamp(2.4rem, 4vw, 3.2rem)',
                  fontWeight: 600,
                  color: '#22252A',
                  marginBottom: 16,
                  letterSpacing: '-0.02em',
                }}
              >
                The Quantum <span className="atlas-marker">Atlas Entries</span>
              </h2>

              <p
                style={{
                  color: '#5A6578',
                  fontSize: 16.5,
                  maxWidth: 580,
                  margin: '0 auto',
                  lineHeight: 1.6,
                }}
              >
                Curated, approachable deep dives into the foundational phenomena, algorithms, and physical architectures
                shaping the quantum future.
              </p>
            </div>

            {/* Concept Atlas Component */}
            <ConceptAtlas />
          </div>
        </section>

        {/* ══════════════════════════════════════════════
            SECTION 4: LEARNING ROADMAP TEASER → /roadmap
        ══════════════════════════════════════════════ */}
        <section
          id="roadmap"
          style={{
            padding: '110px 28px',
            background: '#E6EBE0',
            borderTop: '1px solid #D5DDD0',
            borderBottom: '1px solid #D5DDD0',
          }}
        >
          <div style={{ maxWidth: 1180, margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: 48 }}>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 7,
                  padding: '6px 15px',
                  borderRadius: 999,
                  background: 'rgba(255, 255, 255, 0.7)',
                  border: '1px solid #D5DDD0',
                  fontSize: 12.5,
                  fontWeight: 700,
                  marginBottom: 18,
                  letterSpacing: '0.02em',
                }}
              >
                <Compass size={13} color="#ED6A5A" /> {TOTAL_MILESTONES} MILESTONES ·{' '}
                {TOTAL_RESOURCES} RESOURCES
              </div>

              <h2
                style={{
                  fontFamily: "'Exo 2', sans-serif",
                  fontSize: 'clamp(2.4rem, 4vw, 3.2rem)',
                  fontWeight: 600,
                  color: '#22252A',
                  marginBottom: 16,
                  letterSpacing: '-0.02em',
                }}
              >
                The Quantum <span className="atlas-marker">Learning Roadmap</span>
              </h2>
              <p
                style={{
                  fontFamily: "'Lora', serif",
                  fontSize: 19,
                  color: '#475569',
                  maxWidth: 620,
                  margin: '0 auto',
                  lineHeight: 1.55,
                }}
              >
                Three tracks from your first qubit to reading papers — with every book, course, tool
                and paper you need at each step.
              </p>
            </div>

            <div className="roadmap-grid-3" style={{ marginBottom: 40 }}>
              {TRACKS.map((t) => (
                <Link
                  key={t.id}
                  href="/roadmap"
                  className="atlas-card"
                  style={{
                    padding: 28,
                    background: '#FFFFFF',
                    textDecoration: 'none',
                    display: 'flex',
                    flexDirection: 'column',
                    height: '100%',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: 12,
                    }}
                  >
                    <div>
                      <div
                        style={{
                          fontSize: 11,
                          fontWeight: 800,
                          letterSpacing: '0.07em',
                          textTransform: 'uppercase',
                          color: t.accent,
                          marginBottom: 4,
                        }}
                      >
                        {t.label}
                      </div>
                      <div
                        style={{
                          fontFamily: "'Exo 2', sans-serif",
                          fontSize: 24,
                          fontWeight: 700,
                          color: '#22252A',
                          lineHeight: 1.2,
                        }}
                      >
                        {t.subtitle}
                      </div>
                      <div style={{ fontSize: 12.5, color: '#5A6578', marginTop: 6 }}>
                        {t.duration} · {t.commitment}
                      </div>
                    </div>
                    <Stickman pose={t.mascotPose} size={76} accent={t.accent} style={{ flexShrink: 0 }} />
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 9,
                      margin: '20px 0',
                      flex: 1,
                    }}
                  >
                    {t.milestones.slice(0, 3).map((m) => (
                      <div key={m.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 9 }}>
                        <CheckCircle2
                          size={15}
                          color={t.accent}
                          style={{ flexShrink: 0, marginTop: 2 }}
                        />
                        <span style={{ fontSize: 13.5, color: '#22252A', lineHeight: 1.5 }}>
                          {m.title}
                        </span>
                      </div>
                    ))}
                    <div style={{ fontSize: 12.5, color: '#5A6578', paddingLeft: 24 }}>
                      + {t.milestones.length - 3} more milestones
                    </div>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: 10,
                      paddingTop: 16,
                      borderTop: '1px solid #E2E6DF',
                    }}
                  >
                    <span
                      style={{
                        fontSize: 11.5,
                        fontWeight: 700,
                        color: t.accentInk,
                        background: t.accentSoft,
                        padding: '5px 10px',
                        borderRadius: 7,
                      }}
                    >
                      {RESOURCES.filter((r) => r.level === t.id).length} resources
                    </span>
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                        fontFamily: "'Exo 2', sans-serif",
                        fontSize: 13.5,
                        fontWeight: 700,
                        color: t.accent,
                      }}
                    >
                      View full roadmap <ArrowRight size={14} />
                    </span>
                  </div>
                </Link>
              ))}
            </div>

            <div style={{ textAlign: 'center' }}>
              <Link href="/roadmap" className="btn-atlas-coral">
                <Compass size={16} /> Open the full roadmap
              </Link>
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════
            SECTION 5: TESTIMONIALS (Academic distinction)
        ══════════════════════════════════════════════ */}
        <section style={{ padding: '110px 28px', background: '#FAFAF8' }}>
          <div style={{ maxWidth: 1180, margin: '0 auto' }}>
            <h2
              style={{
                fontFamily: "'Exo 2', sans-serif",
                fontSize: 'clamp(2.2rem, 3.5vw, 2.8rem)',
                fontWeight: 600,
                color: '#22252A',
                textAlign: 'center',
                marginBottom: 54,
              }}
            >
              Created for <span className="atlas-marker">Curious Minds</span> & Future Physicists
            </h2>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 28,
              }}
            >
              {TESTIMONIALS.map((t, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1, duration: 0.5 }}
                  viewport={{ once: true }}
                >
                  <div
                    className="atlas-card"
                    style={{
                      padding: 28,
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      background: '#FFFFFF',
                    }}
                  >
                    <p
                      style={{
                        fontFamily: "'Lora', serif",
                        fontSize: 15,
                        lineHeight: 1.7,
                        color: '#3A3F47',
                        fontStyle: 'italic',
                        marginBottom: 20,
                      }}
                    >
                      &ldquo;{t.quote}&rdquo;
                    </p>

                    <div>
                      <div style={{ fontFamily: "'Exo 2', sans-serif", fontWeight: 700, fontSize: 15, color: '#22252A' }}>
                        {t.name}
                      </div>
                      <div style={{ fontSize: 12.5, color: '#5A6578', marginTop: 2 }}>{t.affiliation}</div>
                      <div style={{ fontSize: 11, color: '#ED6A5A', fontWeight: 600, marginTop: 4 }}>{t.role}</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════
            INSTITUTIONAL FOOTER (Quantum Atlas Aesthetic)
        ══════════════════════════════════════════════ */}
        <footer
          style={{
            background: '#9BC1BC',
            color: '#22252A',
            padding: '70px 28px 40px',
            borderTop: '1px solid #7FAFA9',
          }}
        >
          <div style={{ maxWidth: 1180, margin: '0 auto' }}>
            {/* Top row: Brand + Description + Links */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
                gap: 40,
                marginBottom: 50,
              }}
            >
              <div>
                <AtlasLogo size={38} showText={true} />
                <p style={{ fontSize: 14, color: '#22252A', lineHeight: 1.65, marginTop: 16, maxWidth: 320 }}>
                  The Qurio Atlas is an approachable, interactive multimedia atlas of quantum physics and quantum computing
                  built for students, researchers, and developers.
                </p>
              </div>

              <div>
                <h4 style={{ fontFamily: "'Exo 2', sans-serif", fontWeight: 700, fontSize: 15, marginBottom: 14 }}>
                  Atlas Sections
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 14 }}>
                  <a href="#start" style={{ color: '#22252A', textDecoration: 'none' }}>
                    Get Started
                  </a>
                  <a href="#entries" style={{ color: '#22252A', textDecoration: 'none' }}>
                    Concept Entries
                  </a>
                  <a href="#interactives" style={{ color: '#22252A', textDecoration: 'none' }}>
                    Wave & State Interactives
                  </a>
                  <Link href="/roadmap" style={{ color: '#22252A', textDecoration: 'none' }}>
                    Learning Roadmap
                  </Link>
                  <Link href="/qubit" style={{ color: '#22252A', textDecoration: 'none' }}>
                    Qurio Qubit Arcade
                  </Link>
                  <Link href="/profile" style={{ color: '#22252A', textDecoration: 'none' }}>
                    My Progress
                  </Link>
                </div>
              </div>

              <div>
                <h4 style={{ fontFamily: "'Exo 2', sans-serif", fontWeight: 700, fontSize: 15, marginBottom: 14 }}>
                  Studios & Tools
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 14 }}>
                  <Link href="/circuit" style={{ color: '#22252A', textDecoration: 'none' }}>
                    Circuit Studio
                  </Link>
                  <Link href="/simulate" style={{ color: '#22252A', textDecoration: 'none' }}>
                    3D Bloch Simulator
                  </Link>
                  <Link href="/ai-tutor" style={{ color: '#22252A', textDecoration: 'none' }}>
                    AI Quantum Tutor
                  </Link>
                  <Link href="/career" style={{ color: '#22252A', textDecoration: 'none' }}>
                    Career Navigator
                  </Link>
                  <Link href="/leaderboard" style={{ color: '#22252A', textDecoration: 'none' }}>
                    Global Leaderboard
                  </Link>
                </div>
              </div>

              <div>
                <h4 style={{ fontFamily: "'Exo 2', sans-serif", fontWeight: 700, fontSize: 15, marginBottom: 14 }}>
                  Community & Research
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 14 }}>
                  <span style={{ color: '#22252A' }}>Smart India Hackathon 2026</span>
                  <span style={{ color: '#22252A' }}>Open-Source Qiskit Compatible</span>
                  <span style={{ color: '#22252A' }}>Reference: quantumatlas.umd.edu</span>
                  <a
                    href="mailto:contact@qurio.ai"
                    style={{ color: '#22252A', textDecoration: 'underline', marginTop: 4 }}
                  >
                    Send Feedback & Ideas
                  </a>
                </div>
              </div>
            </div>

            {/* Bottom row */}
            <div
              style={{
                borderTop: '1px solid rgba(34, 37, 42, 0.15)',
                paddingTop: 24,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: 16,
                fontSize: 13,
                color: '#22252A',
              }}
            >
              <div>
                © 2026 The Qurio Atlas · Inspired by the Joint Quantum Institute (JQI) Quantum Atlas 
              </div>

              <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                <Link href="/learn" style={{ color: '#22252A', textDecoration: 'none' }}>
                  Privacy & Terms
                </Link>
                <Link href="/login#signup" style={{ color: '#22252A', textDecoration: 'none', fontWeight: 600 }}>
                  Enter Learning Dashboard →
                </Link>
              </div>
            </div>
          </div>
        </footer>
      </div >
    </div >
  );
}
