import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "react-router-dom";
import Cookies from "js-cookie";
import debounce from "lodash.debounce";
import './component_styles/products.css';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");  // Add state for search query
  const [isEmpty, setIsEmpty] = useState(false); // No results flag
  const [isLoading, setIsLoading] = useState(false); // Loading state
  const location = useLocation();

  // Extract initial category filter from query parameters
  useEffect(() => {
    const query = new URLSearchParams(location.search);
    const initialCategory = query.get("category");

    if (initialCategory) {
      // If category filter is set, use it as the selected categories
      setSelectedCategories(initialCategory.split(","));
    } else {
      // If no category filter is set, check all checkboxes by default
      setSelectedCategories([]);
    }
  }, [location.search, categories]);

  // Fetch categories for the dropdown
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const token = Cookies.get("access_token");

        const response = await fetch("http://127.0.0.1:8000/api/categories/", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch categories.");
        }

        const data = await response.json();
        setCategories(data);
      } catch (error) {
        console.error("Error fetching categories:", error);
        setError("Failed to fetch categories. Please try again.");
      }
    };

    fetchCategories();
  }, []);

  // Debounced function to fetch products
  const fetchProducts = useCallback(
    debounce(async (query, categories, page) => {
      setIsLoading(true);
      setError(null);
  
      try {
        const token = Cookies.get("access_token");
        if (!token) {
          throw new Error("No token found. Please log in.");
        }
  
        const apiUrl = new URL("http://127.0.0.1:8000/api/products/");
        const params = { page, category_id: categories.join(","), query };
  
        Object.keys(params).forEach(key => {
          if (params[key]) apiUrl.searchParams.append(key, params[key]);
        });
  
        const response = await fetch(apiUrl, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });
  
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        
        const data = await response.json();
        setProducts(data.results || []);
        setRecommendations(data.recommendations || []);
        setIsEmpty(!data.results.length);
        setTotalPages(Math.ceil(data.count / 10));
      } catch (error) {
        console.error("Error fetching products:", error);
        setError("Failed to fetch products. Please try again.");
      } finally {
        setIsLoading(false);
      }
    }, 500),
    []
  );
  

  // Fetch products on dependency change
  useEffect(() => {
    fetchProducts(searchQuery, selectedCategories, currentPage);
  }, [searchQuery, selectedCategories, currentPage, fetchProducts]);

  const handleCategoryChange = (categoryId) => {
    if (selectedCategories.includes(categoryId)) {
      setSelectedCategories(selectedCategories.filter((id) => id !== categoryId));
    } else {
      setSelectedCategories([...selectedCategories, categoryId]);
    }
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };
  
  return (
    <div>
      <h1 className="header">Products</h1>
      {error && <p className="error-message">{error}</p>}

      {/* Search Bar */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>

      {/* Filter Dropdown */}
      <div className="filter-dropdown">
        <button className="dropdown-button">Filter by Category</button>
        <div className="dropdown-content">
          {categories.map((category) => (
            <label key={category.category_id} className="dropdown-item">
              <input
                type="checkbox"
                checked={selectedCategories.includes(category.category_id.toString())}
                onChange={() => handleCategoryChange(category.category_id.toString())}
              />
              {category.category_name}
            </label>
          ))}
        </div>
      </div>

      {isLoading && <p>Loading...</p>}

      {isEmpty && (
        <div>
          <h3>No Results Found</h3>
          {recommendations.length > 0 && (
            <div>
              <h4>Recommendations:</h4>
              {recommendations.map((rec, index) => (
                <div key={index}>
                  <div><strong>Name:</strong> {rec.name}</div>
                  <div><strong>Description:</strong> {rec.description}</div>
                  <div><strong>Price:</strong> {rec.price}</div>
                  <hr />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {products.length > 0 && (
        <table className="product-table">
          <thead>
            <tr>
              <th>Product ID</th>
              <th>Product Name</th>
              <th>Category</th>
              <th>Available Stock</th>
              <th>Marked Price</th>
              <th>Discount Price</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.product_id}>
                <td>{product.product_id}</td>
                <td>{product.name}</td>
                <td>{product.category_name}</td>
                <td>{product.available_stock}</td>
                <td>{product.marked_price}</td>
                <td>{product.discount_price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="pagination">
        <button
          onClick={() => setCurrentPage(currentPage - 1)}
          disabled={currentPage === 1 || isLoading}
        >
          Previous
        </button>
        <span>
          {currentPage} / {totalPages}
        </span>
        <button
          onClick={() => setCurrentPage(currentPage + 1)}
          disabled={currentPage === totalPages || isLoading}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default Products;
