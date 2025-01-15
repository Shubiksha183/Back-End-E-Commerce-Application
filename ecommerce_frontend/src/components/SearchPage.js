import React, { useState } from "react";
import SearchBar from "./SearchBar";
import SearchResults from "./SearchResults";
import { searchProducts } from "./search";

const SearchPage = () => {
  const [results, setResults] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (query) => {
    setLoading(true);
    setError("");
    setResults([]);
    setRecommendations([]);

    try {
      const data = await searchProducts(query);
      setResults(data.results || []);
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError("Failed to fetch search results. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-page">
      <h1>Search Products</h1>
      <SearchBar onSearch={handleSearch} />

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      <SearchResults results={results} recommendations={recommendations} />
    </div>
  );
};

export default SearchPage;
