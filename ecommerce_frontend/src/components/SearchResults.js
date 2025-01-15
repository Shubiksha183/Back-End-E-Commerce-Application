    import React from 'react';

    const SearchResults = ({ results }) => {
        return (
            <div>
                {results.map((product) => (
                    <div key={product.id}>
                        <h3>{product.name}</h3>
                        <p>Category: {product.category}</p>
                        <p>Brand: {product.brand}</p>
                        <p>{product.description}</p>
                    </div>
                ))}
            </div>
        );
    };

    export default SearchResults;
