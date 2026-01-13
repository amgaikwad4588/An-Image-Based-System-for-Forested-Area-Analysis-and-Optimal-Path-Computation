/**
 * EcoView Database Manager
 * Lightweight IndexedDB wrapper for storing historical analysis data
 * Enhanced with better error handling and fallback mechanisms
 */

class EcoViewDatabase {
    constructor() {
        this.dbName = 'EcoViewDB';
        this.version = 1;
        this.db = null;
        this.isSupported = this.checkSupport();
    }

    // Check if IndexedDB is supported
    checkSupport() {
        try {
            if (!window.indexedDB) {
                console.warn('IndexedDB not supported, falling back to localStorage');
                return false;
            }
            return true;
        } catch (error) {
            console.warn('IndexedDB check failed:', error);
            return false;
        }
    }

    // Initialize the database with enhanced error handling
    async init() {
        if (!this.isSupported) {
            throw new Error('IndexedDB not supported');
        }

        return new Promise((resolve, reject) => {
            try {
                const request = indexedDB.open(this.dbName, this.version);

                request.onerror = () => {
                    console.error('Database failed to open:', request.error);
                    reject(new Error(`Database error: ${request.error?.message || 'Unknown error'}`));
                };

                request.onsuccess = () => {
                    this.db = request.result;
                    console.log('Database opened successfully');
                    
                    // Add error handling for database operations
                    this.db.onerror = (event) => {
                        console.error('Database operation error:', event.target.error);
                    };
                    
                    resolve(this.db);
                };

                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    
                    // Create object stores with better error handling
                    try {
                        if (!db.objectStoreNames.contains('analyses')) {
                            const analysesStore = db.createObjectStore('analyses', { 
                                keyPath: 'id', 
                                autoIncrement: true 
                            });
                            
                            // Create indexes for efficient querying
                            analysesStore.createIndex('date', 'date', { unique: false });
                            analysesStore.createIndex('type', 'type', { unique: false });
                            analysesStore.createIndex('species', 'species', { unique: false });
                            analysesStore.createIndex('confidence', 'confidence', { unique: false });
                        }

                        if (!db.objectStoreNames.contains('settings')) {
                            db.createObjectStore('settings', { keyPath: 'key' });
                        }

                        if (!db.objectStoreNames.contains('metadata')) {
                            db.createObjectStore('metadata', { keyPath: 'key' });
                        }

                        console.log('Database structure created successfully');
                    } catch (error) {
                        console.error('Error creating database structure:', error);
                        reject(error);
                    }
                };

                request.onblocked = () => {
                    console.warn('Database upgrade blocked by another connection');
                    // Try to close any existing connections
                    if (this.db) {
                        this.db.close();
                    }
                };

            } catch (error) {
                console.error('Failed to initialize database:', error);
                reject(error);
            }
        });
    }

    // Add a new analysis record with fallback
    async addAnalysis(analysisData) {
        if (!this.db) {
            return this.addAnalysisToLocalStorage(analysisData);
        }

        const transaction = this.db.transaction(['analyses'], 'readwrite');
        const store = transaction.objectStore('analyses');
        
        const analysis = {
            ...analysisData,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        return new Promise((resolve, reject) => {
            const request = store.add(analysis);
            
            request.onsuccess = () => {
                console.log('Analysis added with ID:', request.result);
                resolve(request.result);
            };
            
            request.onerror = () => {
                console.error('Error adding analysis:', request.error);
                // Fallback to localStorage
                try {
                    const id = this.addAnalysisToLocalStorage(analysis);
                    resolve(id);
                } catch (fallbackError) {
                    reject(fallbackError);
                }
            };
        });
    }

    // Fallback method for localStorage
    addAnalysisToLocalStorage(analysisData) {
        try {
            const stored = localStorage.getItem('ecoview_historical_data');
            const analyses = stored ? JSON.parse(stored) : [];
            
            const analysis = {
                id: Date.now(), // Simple ID generation
                ...analysisData,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            
            analyses.push(analysis);
            localStorage.setItem('ecoview_historical_data', JSON.stringify(analyses));
            
            console.log('Analysis added to localStorage with ID:', analysis.id);
            return analysis.id;
        } catch (error) {
            console.error('Error adding to localStorage:', error);
            throw error;
        }
    }

    // Get all analyses with optional filtering and fallback
    async getAnalyses(filters = {}) {
        if (!this.db) {
            return this.getAnalysesFromLocalStorage(filters);
        }

        const transaction = this.db.transaction(['analyses'], 'readonly');
        const store = transaction.objectStore('analyses');
        
        return new Promise((resolve, reject) => {
            const request = store.getAll();
            
            request.onsuccess = () => {
                let analyses = request.result;
                
                // Apply filters
                analyses = this.applyFilters(analyses, filters);
                
                // Sort by date (newest first)
                analyses.sort((a, b) => new Date(b.date) - new Date(a.date));
                
                resolve(analyses);
            };
            
            request.onerror = () => {
                console.error('Error getting analyses:', request.error);
                // Fallback to localStorage
                try {
                    const analyses = this.getAnalysesFromLocalStorage(filters);
                    resolve(analyses);
                } catch (fallbackError) {
                    reject(fallbackError);
                }
            };
        });
    }

    // Fallback method for getting analyses from localStorage
    getAnalysesFromLocalStorage(filters = {}) {
        try {
            const stored = localStorage.getItem('ecoview_historical_data');
            const analyses = stored ? JSON.parse(stored) : [];
            
            // Apply filters
            const filteredAnalyses = this.applyFilters(analyses, filters);
            
            // Sort by date (newest first)
            filteredAnalyses.sort((a, b) => new Date(b.date) - new Date(a.date));
            
            return filteredAnalyses;
        } catch (error) {
            console.error('Error getting from localStorage:', error);
            return [];
        }
    }

    // Apply filters to analyses array
    applyFilters(analyses, filters) {
        let filtered = [...analyses];
        
        if (filters.startDate) {
            filtered = filtered.filter(a => a.date >= filters.startDate);
        }
        if (filters.endDate) {
            filtered = filtered.filter(a => a.date <= filters.endDate);
        }
        if (filters.type) {
            filtered = filtered.filter(a => a.type === filters.type);
        }
        if (filters.species) {
            filtered = filtered.filter(a => a.species === filters.species);
        }
        if (filters.minConfidence) {
            filtered = filtered.filter(a => a.confidence >= filters.minConfidence);
        }
        
        return filtered;
    }

    // Get analysis by ID
    async getAnalysis(id) {
        const transaction = this.db.transaction(['analyses'], 'readonly');
        const store = transaction.objectStore('analyses');
        
        return new Promise((resolve, reject) => {
            const request = store.get(id);
            
            request.onsuccess = () => {
                resolve(request.result);
            };
            
            request.onerror = () => {
                console.error('Error getting analysis:', request.error);
                reject(request.error);
            };
        });
    }

    // Update an existing analysis
    async updateAnalysis(id, updateData) {
        const transaction = this.db.transaction(['analyses'], 'readwrite');
        const store = transaction.objectStore('analyses');
        
        return new Promise((resolve, reject) => {
            const getRequest = store.get(id);
            
            getRequest.onsuccess = () => {
                const analysis = getRequest.result;
                if (analysis) {
                    const updatedAnalysis = {
                        ...analysis,
                        ...updateData,
                        updatedAt: new Date().toISOString()
                    };
                    
                    const putRequest = store.put(updatedAnalysis);
                    
                    putRequest.onsuccess = () => {
                        console.log('Analysis updated:', id);
                        resolve(updatedAnalysis);
                    };
                    
                    putRequest.onerror = () => {
                        console.error('Error updating analysis:', putRequest.error);
                        reject(putRequest.error);
                    };
                } else {
                    reject(new Error('Analysis not found'));
                }
            };
            
            getRequest.onerror = () => {
                console.error('Error getting analysis for update:', getRequest.error);
                reject(getRequest.error);
            };
        });
    }

    // Delete an analysis
    async deleteAnalysis(id) {
        const transaction = this.db.transaction(['analyses'], 'readwrite');
        const store = transaction.objectStore('analyses');
        
        return new Promise((resolve, reject) => {
            const request = store.delete(id);
            
            request.onsuccess = () => {
                console.log('Analysis deleted:', id);
                resolve(true);
            };
            
            request.onerror = () => {
                console.error('Error deleting analysis:', request.error);
                reject(request.error);
            };
        });
    }

    // Get analytics data
    async getAnalytics() {
        const analyses = await this.getAnalyses();
        
        const analytics = {
            totalAnalyses: analyses.length,
            speciesCount: new Set(analyses.filter(a => a.species).map(a => a.species)).size,
            averageConfidence: 0,
            mostCommonSpecies: null,
            analysesByType: {},
            analysesByDate: {},
            recentAnalyses: analyses.slice(0, 10)
        };

        // Calculate average confidence
        const speciesAnalyses = analyses.filter(a => a.confidence !== null && a.confidence !== undefined);
        if (speciesAnalyses.length > 0) {
            analytics.averageConfidence = speciesAnalyses.reduce((sum, a) => sum + a.confidence, 0) / speciesAnalyses.length;
        }

        // Find most common species
        const speciesFreq = {};
        analyses.filter(a => a.species).forEach(a => {
            speciesFreq[a.species] = (speciesFreq[a.species] || 0) + 1;
        });
        analytics.mostCommonSpecies = Object.keys(speciesFreq).reduce((a, b) => 
            speciesFreq[a] > speciesFreq[b] ? a : b, null);

        // Group by type
        analyses.forEach(a => {
            analytics.analysesByType[a.type] = (analytics.analysesByType[a.type] || 0) + 1;
        });

        // Group by date
        analyses.forEach(a => {
            const date = a.date.split('T')[0]; // Get date part only
            analytics.analysesByDate[date] = (analytics.analysesByDate[date] || 0) + 1;
        });

        return analytics;
    }

    // Clear all data
    async clearAllData() {
        const transaction = this.db.transaction(['analyses'], 'readwrite');
        const store = transaction.objectStore('analyses');
        
        return new Promise((resolve, reject) => {
            const request = store.clear();
            
            request.onsuccess = () => {
                console.log('All analyses cleared');
                resolve(true);
            };
            
            request.onerror = () => {
                console.error('Error clearing data:', request.error);
                reject(request.error);
            };
        });
    }

    // Export data
    async exportData(format = 'json') {
        const analyses = await this.getAnalyses();
        
        if (format === 'csv') {
            const headers = ['ID', 'Date', 'Type', 'Species', 'Confidence', 'Green Cover', 'Tree Count', 'Created At'];
            const csvContent = [
                headers.join(','),
                ...analyses.map(a => [
                    a.id,
                    a.date,
                    a.type,
                    a.species || '',
                    a.confidence || '',
                    a.metadata?.greenCover || '',
                    a.metadata?.treeCount || '',
                    a.createdAt
                ].join(','))
            ].join('\n');
            
            return csvContent;
        } else {
            return JSON.stringify(analyses, null, 2);
        }
    }

    // Import data
    async importData(data, format = 'json') {
        let analyses;
        
        if (format === 'json') {
            analyses = JSON.parse(data);
        } else if (format === 'csv') {
            const lines = data.split('\n');
            const headers = lines[0].split(',');
            analyses = lines.slice(1).map(line => {
                const values = line.split(',');
                const analysis = {};
                headers.forEach((header, index) => {
                    analysis[header.toLowerCase().replace(/\s+/g, '')] = values[index];
                });
                return analysis;
            });
        }

        // Add all analyses
        for (const analysis of analyses) {
            try {
                await this.addAnalysis(analysis);
            } catch (error) {
                console.error('Error importing analysis:', error);
            }
        }

        return analyses.length;
    }

    // Get database statistics
    async getStats() {
        const transaction = this.db.transaction(['analyses'], 'readonly');
        const store = transaction.objectStore('analyses');
        
        return new Promise((resolve, reject) => {
            const request = store.count();
            
            request.onsuccess = () => {
                resolve({
                    totalRecords: request.result,
                    databaseSize: this.getDatabaseSize(),
                    lastUpdated: new Date().toISOString()
                });
            };
            
            request.onerror = () => {
                console.error('Error getting stats:', request.error);
                reject(request.error);
            };
        });
    }

    // Estimate database size
    getDatabaseSize() {
        if (navigator.storage && navigator.storage.estimate) {
            navigator.storage.estimate().then(estimate => {
                return estimate.usage || 0;
            });
        }
        return 0;
    }
}

// Create global instance
window.ecoviewDB = new EcoViewDatabase();

// Initialize database when DOM is loaded with enhanced error handling
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await window.ecoviewDB.init();
        console.log('EcoView Database initialized successfully');
    } catch (error) {
        console.warn('Failed to initialize IndexedDB:', error.message);
        console.log('Using localStorage fallback mode');
        
        // Set up localStorage fallback mode
        window.ecoviewDB.db = null;
        window.ecoviewDB.isSupported = false;
        
        // Initialize with sample data if localStorage is empty
        const stored = localStorage.getItem('ecoview_historical_data');
        if (!stored) {
            const sampleData = [
                {
                    id: Date.now(),
                    date: '2025-01-15',
                    type: 'species',
                    species: 'Oak',
                    confidence: 0.85,
                    image: 'data:image/jpeg;base64,...',
                    metadata: { greenCover: 75, treeCount: 12 },
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                },
                {
                    id: Date.now() + 1,
                    date: '2025-01-14',
                    type: 'path',
                    species: null,
                    confidence: null,
                    image: 'data:image/jpeg;base64,...',
                    metadata: { pathLength: 150, efficiency: 0.92 },
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                },
                {
                    id: Date.now() + 2,
                    date: '2025-01-13',
                    type: 'species',
                    species: 'Pine',
                    confidence: 0.92,
                    image: 'data:image/jpeg;base64,...',
                    metadata: { greenCover: 88, treeCount: 8 },
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                }
            ];
            
            localStorage.setItem('ecoview_historical_data', JSON.stringify(sampleData));
            console.log('Sample data added to localStorage');
        }
    }
});
