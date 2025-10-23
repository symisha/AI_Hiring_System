import React from 'react';

type RevealProps = React.PropsWithChildren<{
  className?: string;
  rootMargin?: string;
  threshold?: number;
  delay?: number; // ms
}>;

const Reveal: React.FC<RevealProps> = ({ children, className = '', rootMargin = '0px', threshold = 0.15, delay = 0 }) => {
  const ref = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            window.setTimeout(() => el.classList.add('reveal-visible'), delay);
            obs.unobserve(el);
          }
        });
      },
      { root: null, rootMargin, threshold }
    );

    el.classList.add('reveal');
    obs.observe(el);

    return () => obs.disconnect();
  }, [rootMargin, threshold, delay]);

  // Use an explicit inline transition to ensure consistent timing regardless of Tailwind config
  const transitionStyle: React.CSSProperties = {
    transition: 'transform 900ms cubic-bezier(0.2, 0.8, 0.2, 1), opacity 900ms cubic-bezier(0.2, 0.8, 0.2, 1)'
  };

  return (
    <div ref={ref} style={transitionStyle} className={`${className}`}>
      {children}
    </div>
  );
};

export default Reveal;
