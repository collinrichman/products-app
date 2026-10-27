import { useEffect, useState, type FormEvent } from "react";
import type { Product } from "./types";

async function fetchProducts(): Promise<Product[]> {
  const res = await fetch("/api/products");
  return res.json();
}

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProducts().then(setProducts);
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const res = await fetch("/api/products", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name }),
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    setError(null);
    setName("");
    setProducts(await fetchProducts());
  }

  return (
    <main>
      <h1>Products</h1>
      <form onSubmit={handleSubmit}>
        <input value={name} onChange={(e) => setName(e.target.value)} />
        <button type="submit" disabled={!name.trim()}>
          Create
        </button>
      </form>
      {error && <p>{error}</p>}
      <ul>
        {products.map((product) => (
          <li key={product.id}>{product.name}</li>
        ))}
      </ul>
    </main>
  );
}
