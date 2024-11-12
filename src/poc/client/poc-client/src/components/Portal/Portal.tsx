import React from 'react'
import Image from 'next/image'
import styles from './portal.module.css';
import { useRouter } from 'next/navigation';


const Portal = () => {
    const router = useRouter();

    const goToNextPage = () => {
        router.push('/portal'); // placeholder for next page
    };

    return (
        <div className={styles.container}>
            {/* Logo */}
        
            {/* Header Section */}
            <header className={styles.header}>
                <h1>ITB 159 Station Portal</h1>
            </header>
            <Image
                className={styles.logo}
                src="/ITB159.png"
                alt="Station ITB 159 Satellite view"
                width={793}
                height={575}
                priority
            />
            <h1 className={styles.header}>
                Floor Plan
            </h1>
            <h1 className={styles.header}>
                Entry Exit Procedures
            </h1>

            {/* Portal button */}
           
        </div>
    );
}

export default Portal