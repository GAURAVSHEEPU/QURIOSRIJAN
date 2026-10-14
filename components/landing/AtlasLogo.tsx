'use client';
import Link from 'next/link';
import Image from 'next/image';

export interface AtlasLogoProps {
  size?: number;
  showText?: boolean;
}

export default function AtlasLogo({ size = 48, showText = true }: AtlasLogoProps) {
  return (
    <Link
      href="/"
      aria-label="Qurio Atlas home"
      style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center' }}
    >
      <div
        style={{
          width: size * 6,
          height: size * 2.5,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Image
          src="/qurio-logo.jpeg"
          alt="Qurio - Where curiosity meets quantum"
          fill
          sizes={`${size * 4}px`}
          style={{ objectFit: 'cover', objectPosition: 'center' }}
          priority
          unoptimized
        />
      </div>
    </Link>
  );
}
