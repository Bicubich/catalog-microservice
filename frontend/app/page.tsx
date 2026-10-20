'use client';

import { useEffect, useState } from 'react';

interface Product {
  id: string;
  title: string;
  image_url: string;
}

export default function CatalogPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    fetch(`${apiUrl}/products`)
      .then((res) => res.json())
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Ошибка при загрузке каталога:', err);
        setLoading(false);
      });
  }, []);

  return (
    <main>
      <h1>Каталог</h1>
      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <ul>
          {products.map((product) => (
            <li key={product.id}>
              <h3>{product.title}</h3>
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.title}
                  style={{ maxWidth: '200px', display: 'block' }}
                />
              )}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
