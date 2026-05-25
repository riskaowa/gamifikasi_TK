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
            audioEl.currentTime = 0;
            audioEl.loop = loop;
            audioEl.playsInline = true;
            audioEl.autoplay = true;

            // Hybrid strategy for maximum browser compatibility:
            // 1. Start with muted=true (most compatible with autoplay policy)
            // 2. Try to unmute immediately after play starts
            // 3. If unmute fails, use volume=0 (silent) as fallback
            // 4. On user gesture, raise to full volume

            this.log(`Playing "${audioEl.id}" with muted autoplay strategy`);
            audioEl.muted = true;
            audioEl.volume = volume;

            let playPromise = audioEl.play();
            if (playPromise && typeof playPromise.then === 'function') {
                await playPromise;
                this.log(`✓ "${audioEl.id}" started (muted)`);

                // Audio is now playing (muted). Attempt to unmute immediately.
                // This works in many cases because user gesture isn't required for unmute
                // immediately after a successful play().
                setTimeout(async () => {
                    try {
                        audioEl.muted = false;
                        this.log(`✓ "${audioEl.id}" unmuted immediately`);
                        onSuccess && onSuccess();
                    } catch (unmuteError) {
                        // If unmute fails, fall back to volume=0 strategy
                        this.warn(`Unmute failed, using volume=0 fallback:`, unmuteError.message);
                        audioEl.volume = 0;
                        audioEl.muted = false;
                        this.log(`✓ "${audioEl.id}" using volume=0 silent playback`);
                        onSuccess && onSuccess();
                    }
                }, 50);

                return true;
            }

            // Fallback: play() didn't return promise, try direct unmute
            this.log(`"${audioEl.id}" play() did not return promise, attempting unmute`);
            setTimeout(() => {
                try {
                    audioEl.muted = false;
                    this.log(`✓ "${audioEl.id}" unmuted (fallback)`);
                    onSuccess && onSuccess();
                } catch (err) {
                    this.warn(`Could not unmute "${audioEl.id}":`, err.message);
                    audioEl.volume = 0;
                    onSuccess && onSuccess();
                }
            }, 50);

            return true;
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
    playOncePerDay(audioEl, storageKey, options = {}) {
        const today = new Date().toDateString();
        let stored = '';

        try {
            stored = localStorage.getItem(storageKey);
        } catch (storageError) {
            this.warn(`localStorage unavailable for "${storageKey}":`, storageError.message);
        }

        const [lastDate, playCount] = (stored || '').split('|');

        if (lastDate === today) {
            this.log(`"${storageKey}" already played today, skipping`);
            return;
        }

        this.playAudio(audioEl, {
            ...options,
            onSuccess: () => {
                try {
                    localStorage.setItem(storageKey, `${today}|1`);
                } catch (storageError) {
                    this.warn(`Failed to store play state for "${storageKey}":`, storageError.message);
                }
                this.log(`"${storageKey}" marked as played today`);
                options.onSuccess && options.onSuccess();
            },
            onError: (err) => {
                this.warn(`Failed to play "${storageKey}":`, err);
                options.onError && options.onError(err);
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
