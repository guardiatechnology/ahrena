import { useState } from "react";

interface HelloProps {
  default_name?: string;
  greeting?: string;
}

export function Hello({ default_name = "world", greeting = "Hello" }: HelloProps): JSX.Element {
  const [name, setName] = useState<string>(default_name);

  return (
    <div role="region" aria-label="Hello widget">
      <label htmlFor="hello-name">Name</label>
      <input
        id="hello-name"
        type="text"
        value={name}
        onChange={(event) => setName(event.target.value)}
      />
      <p>
        {greeting}, {name}!
      </p>
    </div>
  );
}

export default Hello;
