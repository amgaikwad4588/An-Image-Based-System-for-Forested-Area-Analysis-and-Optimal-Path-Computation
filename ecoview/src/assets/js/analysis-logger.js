/**
 * EcoView Analysis Logger
 * Utility functions for logging analysis results to the database
 */

class AnalysisLogger {
    constructor() {
        this.db = null;
    }

    // Initialize the logger with database connection
    async init() {
        this.db = window.ecoviewDB;
        if (!this.db) {
            console.warn('Database not available, analysis logging disabled');
            return false;
        }
        return true;
    }

    // Log a species identification analysis
    async logSpeciesAnalysis(data) {
        if (!this.db) return false;

        const analysisData = {
            date: new Date().toISOString().split('T')[0],
            type: 'species',
            species: data.species || null,
            confidence: data.confidence || null,
            image: data.image || null,
            metadata: {
                greenCover: data.greenCover || null,
                treeCount: data.treeCount || null,
                boundingBoxes: data.boundingBoxes || null,
                processingTime: data.processingTime || null
            }
        };

        try {
            const id = await this.db.addAnalysis(analysisData);
            console.log('Species analysis logged with ID:', id);
            return id;
        } catch (error) {
            console.error('Error logging species analysis:', error);
            return false;
        }
    }

    // Log a tree counting analysis
    async logTreeCountAnalysis(data) {
        if (!this.db) return false;

        const analysisData = {
            date: new Date().toISOString().split('T')[0],
            type: 'count',
            species: null,
            confidence: data.confidence || null,
            image: data.image || null,
            metadata: {
                treeCount: data.treeCount || 0,
                greenCover: data.greenCover || null,
                processingTime: data.processingTime || null,
                algorithm: data.algorithm || 'default'
            }
        };

        try {
            const id = await this.db.addAnalysis(analysisData);
            console.log('Tree count analysis logged with ID:', id);
            return id;
        } catch (error) {
            console.error('Error logging tree count analysis:', error);
            return false;
        }
    }

    // Log an optimal path analysis
    async logPathAnalysis(data) {
        if (!this.db) return false;

        const analysisData = {
            date: new Date().toISOString().split('T')[0],
            type: 'path',
            species: null,
            confidence: data.efficiency || null,
            image: data.image || null,
            metadata: {
                pathLength: data.pathLength || null,
                efficiency: data.efficiency || null,
                waypoints: data.waypoints || null,
                processingTime: data.processingTime || null,
                algorithm: data.algorithm || 'default'
            }
        };

        try {
            const id = await this.db.addAnalysis(analysisData);
            console.log('Path analysis logged with ID:', id);
            return id;
        } catch (error) {
            console.error('Error logging path analysis:', error);
            return false;
        }
    }

    // Log a green cover analysis
    async logGreenCoverAnalysis(data) {
        if (!this.db) return false;

        const analysisData = {
            date: new Date().toISOString().split('T')[0],
            type: 'greencover',
            species: null,
            confidence: data.confidence || null,
            image: data.image || null,
            metadata: {
                greenCover: data.greenCover || null,
                vegetationDensity: data.vegetationDensity || null,
                processingTime: data.processingTime || null,
                algorithm: data.algorithm || 'default'
            }
        };

        try {
            const id = await this.db.addAnalysis(analysisData);
            console.log('Green cover analysis logged with ID:', id);
            return id;
        } catch (error) {
            console.error('Error logging green cover analysis:', error);
            return false;
        }
    }

    // Generic analysis logger
    async logAnalysis(type, data) {
        if (!this.db) return false;

        const analysisData = {
            date: new Date().toISOString().split('T')[0],
            type: type,
            species: data.species || null,
            confidence: data.confidence || null,
            image: data.image || null,
            metadata: data.metadata || {}
        };

        try {
            const id = await this.db.addAnalysis(analysisData);
            console.log(`${type} analysis logged with ID:`, id);
            return id;
        } catch (error) {
            console.error(`Error logging ${type} analysis:`, error);
            return false;
        }
    }

    // Get recent analyses for a specific type
    async getRecentAnalyses(type = null, limit = 10) {
        if (!this.db) return [];

        try {
            const filters = type ? { type } : {};
            const analyses = await this.db.getAnalyses(filters);
            return analyses.slice(0, limit);
        } catch (error) {
            console.error('Error getting recent analyses:', error);
            return [];
        }
    }

    // Get analysis statistics
    async getStats() {
        if (!this.db) return null;

        try {
            return await this.db.getAnalytics();
        } catch (error) {
            console.error('Error getting analysis stats:', error);
            return null;
        }
    }
}

// Create global instance
window.analysisLogger = new AnalysisLogger();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    await window.analysisLogger.init();
});

// Utility functions for easy access
window.logSpeciesAnalysis = async (data) => {
    return await window.analysisLogger.logSpeciesAnalysis(data);
};

window.logTreeCountAnalysis = async (data) => {
    return await window.analysisLogger.logTreeCountAnalysis(data);
};

window.logPathAnalysis = async (data) => {
    return await window.analysisLogger.logPathAnalysis(data);
};

window.logGreenCoverAnalysis = async (data) => {
    return await window.analysisLogger.logGreenCoverAnalysis(data);
};

window.logAnalysis = async (type, data) => {
    return await window.analysisLogger.logAnalysis(type, data);
};
