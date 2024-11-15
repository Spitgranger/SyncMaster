import React from 'react'
import Image from 'next/image'
import styles from './landing.module.css';
import { useRouter } from 'next/navigation';
import getGeolocation from '@/utils/getLocation';


const Landing = ({ onClick }) => {

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
                    <button onClick={onClick} style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}>
                        Contractor Portal
                    </button>
                </section>
            </main>
        </div>
    );
}

export default Landing