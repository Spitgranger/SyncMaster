'use client'
import { useRouter } from 'next/navigation';
import React from 'react';
import styles from './page.module.css';

const LandingPage: React.FC = () => {
  const router = useRouter();

  const goToNextPage = () => {
    router.push('/next'); // Redirects to the "next" page
  };

  return (
    <div className={styles.container}>
      {/* Header Section */}
      <header className={styles.header}>
        <h1>City of Hamilton, Water Division</h1>
        <p>Water, Wastewater & Stormwater Management</p>
      </header>

      {/* Information Sections */}
      <main className={styles.main}>
        <section className={styles.section}>
          <div className={styles.icon}>🛠️</div>
          <button onClick={goToNextPage} style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}>
          Contractor Portal
      </button>
        </section>
      </main>

      {/* Link to the Next Page */}
    </div>
  );
};

export default LandingPage;

