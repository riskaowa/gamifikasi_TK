/**
 * Unified Audio Helper - Standardized audio playback untuk semua halaman
 * Handles autoplay policy, error recovery, dan debugging
 */
const AudioHelper = {
    DEBUG: true, // Set ke false untuk disable logging
    
    log(...args) {
        if (this.DEBUG) {
            console.log('[AudioHelper]', ...args);
        }
    },

    warn(...args) {
        if (this.DEBUG) {
            console.warn('[AudioHelper]', ...args);
        }
    },

    /**
     * Play audio dengan retry logic untuk handle autoplay policy
     * @param {HTMLAudioElement} audioEl - Audio element
     * @param {Object} options - { volume, loop, onSuccess, onError }
     */
    async playAudio(audioEl, options = {}) {
        const {
            volume = 1.0,
            loop = false,
            onSuccess = null,
            onError = null,
            allowMuted = true
        } = options;

        if (!audioEl) {
            this.warn('Audio element not found');
            onError && onError('Element not found');
            return false;
        }

        try {
            // Reset state
            audioEl.currentTime = 0;
            audioEl.volume = volume;
            audioEl.loop = loop;

            // Try 1: Play with muted (always works if browser allows)
            this.log(`Playing "${audioEl.id}" with muted=true`);
            audioEl.muted = true;
            
            let playPromise = audioEl.play();
            if (playPromise && typeof playPromise.then === 'function') {
                await playPromise;
                this.log(`✓ "${audioEl.id}" started (muted)`);

                // Delay 200ms before unmute (ensure playback started)
                setTimeout(() => {
                    if (allowMuted === false) {
                        // Keep muted if required
                        return;
                    }
                    audioEl.muted = false;
                    this.log(`✓ "${audioEl.id}" unmuted`);
                }, 200);

                onSuccess && onSuccess();
                return true;
            }
        } catch (error) {
            this.warn(`Failed to play "${audioEl.id}":`, error.message);
            onError && onError(error);
            return false;
        }
    },

    /**
     * Play audio once per page session
     * @param {HTMLAudioElement} audioEl 
     * @param {string} storageKey - sessionStorage key
     */
    playOncePerSession(audioEl, storageKey) {
        if (sessionStorage.getItem(storageKey) === 'true') {
            this.log(`"${storageKey}" already played this session, skipping`);
            return;
        }

        this.playAudio(audioEl, {
            onSuccess: () => {
                sessionStorage.setItem(storageKey, 'true');
                this.log(`"${storageKey}" marked as played`);
            },
            onError: (err) => {
                this.warn(`Failed to play "${storageKey}":`, err);
            }
        });
    },

    /**
     * Play audio once per calendar day
     * @param {HTMLAudioElement} audioEl 
     * @param {string} storageKey - localStorage key
     */
    playOncePerDay(audioEl, storageKey) {
        const today = new Date().toDateString();
        const stored = localStorage.getItem(storageKey);
        const [lastDate, playCount] = (stored || '').split('|');

        if (lastDate === today) {
            this.log(`"${storageKey}" already played today, skipping`);
            return;
        }

        this.playAudio(audioEl, {
            onSuccess: () => {
                localStorage.setItem(storageKey, `${today}|1`);
                this.log(`"${storageKey}" marked as played today`);
            },
            onError: (err) => {
                this.warn(`Failed to play "${storageKey}":`, err);
            }
        });
    },

    /**
     * Simple immediate play (untuk sound effect)
     * @param {HTMLAudioElement} audioEl
     */
    playSimple(audioEl) {
        if (!audioEl) return;
        
        audioEl.currentTime = 0;
        audioEl.muted = false;
        
        let playPromise = audioEl.play();
        if (playPromise && typeof playPromise.then === 'function') {
            playPromise
                .then(() => {
                    this.log(`✓ "${audioEl.id}" playing`);
                })
                .catch((error) => {
                    this.warn(`Could not play "${audioEl.id}":`, error.message);
                });
        }
    },

    /**
     * Stop audio
     * @param {HTMLAudioElement} audioEl
     */
    stopAudio(audioEl) {
        if (!audioEl) return;
        
        try {
            audioEl.pause();
            audioEl.currentTime = 0;
            this.log(`✓ "${audioEl.id}" stopped`);
        } catch (error) {
            this.warn(`Error stopping "${audioEl.id}":`, error.message);
        }
    }
};

// Export untuk usage di halaman
window.AudioHelper = AudioHelper;
