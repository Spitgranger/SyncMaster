'use client'
import { useRouter } from 'next/navigation';
import Image from 'next/image'
import React from 'react';
import styles from './page.module.css';

const LandingPage: React.FC = () => {
  const router = useRouter();

  const goToNextPage = () => {
    router.push('/next'); // placeholder for next page
  };

  return (
    <div className={styles.container}>
      {/* Logo */}
      <Image
          className={styles.logo}
          src="/hamilton-logo.svg"
          alt="Next.js logo"
          width={500}
          height={100}
          priority
        />
      {/* Header Section */}
      <header className={styles.header}>
        <h1>City of Hamilton, Water Division</h1>
        <p>Water, Wastewater & Stormwater Management</p>
      </header>

      {/* Portal button */}
      <main className={styles.main}>
        <section className={styles.section}>
          <div className={styles.icon}>🛠️</div>
          <button onClick={goToNextPage} style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}>
          Contractor Portal
      </button>
        </section>
      </main>
    </div>
  );
};

export default LandingPage;

