import React, { useState, useCallback } from 'react';
import axios from 'axios';
import debounce from 'lodash.debounce';  // Import debounce
import './component_styles/search.css';

const Search = () => {
    const [q, setq] = useState('');
    const [results, setResults] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [isEmpty, setIsEmpty] = useState(false);
    const [isLoading, setIsLoading] = useState(false); // For loading state
    const [error, setError] = useState(null); // To capture errors

    // Debounced search function
    const handleSearch = useCallback(
        debounce(async (q) => {
            if (!q) return; // Don't search if q is empty

            setIsLoading(true);
            setError(null);  // Reset error state on each new search

            try {
                // Make the GET request to the backend search API
                const response = await axios.get('http://127.0.0.1:8000/api/search/', {
                    params: { q },
                });

                // Check if results are returned
                if (response.data.results && response.data.results.length > 0) {
                    setResults(response.data.results);
                    setRecommendations([]); // Clear recommendations
                    setIsEmpty(false);
                } else {
                    setResults([]);
                    setRecommendations(response.data.recommendations || []);
                    setIsEmpty(true);
                }
            } catch (err) {
                setError('Failed to fetch results. Please try again later.');
                console.error('Search error:', err);
            } finally {
                setIsLoading(false); // Stop loading when request is finished
            }
        }, 500), // Adjust debounce delay as needed (e.g., 500ms)
        [debounce] // Add debounce as a dependency
    );

    // Update q and trigger debounced search
    const handleChange = (e) => {
        setq(e.target.value);
        handleSearch(e.target.value); // Trigger debounced search on input change
    };

    return (
      <div className="search-container">
          <input
              type="text"
              value={q}
              onChange={handleChange}
              placeholder="Search products"
              className="search-input"
          />
          <button
              onClick={() => handleSearch(q)}
              disabled={isLoading || !q}
              className="search-button"
          >
              {isLoading ? 'Searching...' : 'Search'}
          </button>
          {error && <p className="error-message">{error}</p>} {/* Show error message */}
          <div>
              {isLoading && <p className="loading-text">Loading...</p>} {/* Show loading text while fetching data */}
  
              {results.length > 0 && (
                  <div className="results-container">
                      <h3>Search Results:</h3>
                      {results.map((result, index) => (
                          <div key={index} className="result-item">
                              <div><strong>Name:</strong> {result.name}</div>
                              <div><strong>Description:</strong> {result.description}</div>
                              <div><strong>Price:</strong> {result.marked_price}</div>
                              <hr />
                          </div>
                      ))}
                  </div>
              )}
              {isEmpty && (
                  <div className="no-results">
                      <h3>No Results Found</h3>
                      {recommendations.length > 0 && (
                          <div className="recommendations-container">
                              <h4>Recommendations:</h4>
                              {recommendations.map((rec, index) => (
                                  <div key={index} className="recommendation-item">
                                      <div><strong>Name:</strong> {rec.name}</div>
                                      <div><strong>Description:</strong> {rec.description}</div>
                                      <div><strong>Price:</strong> {rec.marked_price}</div>
                                      <hr />
                                  </div>
                              ))}
                          </div>
                      )}
                  </div>
              )}
          </div>
      </div>
  );
  
};

export default Search;
