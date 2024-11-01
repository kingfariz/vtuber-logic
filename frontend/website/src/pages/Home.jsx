import {
  collection,
  getDocs,
  limit,
  orderBy,
  query,
} from "firebase/firestore";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListingItem from "../components/ListingItem";
import { db } from "../firebase";

export default function Home() {
  const [offerListings, setOfferListings] = useState(null);

  useEffect(() => {
    async function fetchListings() {
      try {
        const listingsRef = collection(db, "listings");
        const q = query(
          listingsRef,
          orderBy("timestamp", "desc"),
          limit(20)
        );
        const querySnap = await getDocs(q);
        const listings = [];
        querySnap.forEach((doc) => {
          listings.push({
            id: doc.id,
            data: doc.data(),
          });
        });
        setOfferListings(listings);
      } catch (error) {
        console.log(error);
      }
    }
    fetchListings();
  }, []);

  return (
    <div className="max-w-6xl mx-auto pt-4 space-y-6">
      <h2 className="px-3 text-2xl mt-6 font-semibold">
        Discover Our Perfumes
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {offerListings &&
          offerListings.map((listing) => (
            <Link to={`/listing/${listing.id}`} key={listing.id}>
              <ListingItem
                key={listing.id}
                listing={listing.data}
                id={listing.id}
              />
            </Link>
          ))}
      </div>
    </div>
  );
}
