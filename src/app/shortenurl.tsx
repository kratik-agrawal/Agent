"use client"
import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from '@/components/ui/input';
import useGetShort from './hooks/useGetShort';


export default function Home() {
  const [count, setCount] = useState(0);
  const [url, setUrl] = useState('');
  const [shortUrl, setShortenedUrl] = useState('')

  const reset = () => {
    setCount(0);
  }

  const { fetchShortUrl } = useGetShort({
    url: 'https://example.com',
    url2: 'https://example.com/extra'
  });

  const handleChange = (event) => {
    setUrl(event.target.value)
  }

  const handleShorten = async () => {
    const response = await fetchShortUrl(url)
    setShortenedUrl(response) 
  }

  return (
    <div style={{ padding: '2rem', alignItems: 'center'}}>
      <h1>Demo Component</h1>
      <p>Count is {count}</p>
      <Button onClick={() => setCount(count + 1)}>Increment</Button>
      <Button onClick={reset}>Reset</Button>
      <div>
        <Input 
          placeholder='input url here' 
          value={url}
          onChange={handleChange}
        />
        <Button onClick={handleShorten}>Shorten</Button>

      </div>
      <p> Shortened Url IS {shortUrl}</p>
      

    </div>
  );
}