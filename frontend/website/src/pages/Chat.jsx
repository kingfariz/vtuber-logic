import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { collection, getDocs, query, where } from "firebase/firestore";
import { db } from "../firebase";

export default function Chat() {
  const [liveData, setLiveData] = useState({ live_link: null, name: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchLiveData() {
      try {
        // Reference to the aiAgents collection
        const agentsRef = collection(db, "aiAgents");
        const q = query(agentsRef, where("campaignId", "==", "1"));
        const querySnap = await getDocs(q);

        if (!querySnap.empty) {
          const docData = querySnap.docs[0].data();
          setLiveData({ live_link: docData.live_link, name: docData.name });
        } else {
          toast.error("Campaign not found");
        }
      } catch (error) {
        toast.error("Could not fetch live data");
      } finally {
        setLoading(false);
      }
    }

    fetchLiveData();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-3">
      <h1 className="text-3xl text-center mt-6 font-bold mb-6">
        {liveData.name || "YouTube Live"}
      </h1>
      {loading ? (
        <p>Loading...</p>
      ) : liveData.live_link ? (
        <div className="flex justify-center">
          <iframe
            width="560"
            height="315"
            src={liveData.live_link}
            title={liveData.name || "YouTube Live Stream"}
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
          ></iframe>
        </div>
      ) : (
        <p>SORRY OUR AI VTUBER IS CURRENTLY OFFLINE {liveData.name}</p>
      )}
    </div>
  );
}
