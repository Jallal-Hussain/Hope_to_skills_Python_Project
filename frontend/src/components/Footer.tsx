import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <>
      {/* Enhanced Footer */}
      <footer className="bg-background dark:bg-foreground h-auto lg:h-[65px] w-full py-6 border border-t-secondary border-b-0 border-l-0 border-r-0 transition-colors duration-300 isolate">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-muted-secondary/70 dark:text-muted/80">
            <span className="text-sm">
              © {new Date().getFullYear()} CAG Project-Hope to Skills
            </span>
            <span className="hidden md:block text-sm">All rights reserved</span>
            <div className="flex items-center gap-4">
              <span className="text-sm">
                Developed by{" "}
                <Link
                  to="https://jallalhussain.vercel.app"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium hover:underline hover:text-primary"
                >
                  Jalal Hussain
                </Link>
              </span>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
};

export default Footer;
