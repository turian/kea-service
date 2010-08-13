package patch.main;


import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import kea.filters.KEAFilter;
import kea.main.KEAKeyphraseExtractor;
import kea.stemmers.PorterStemmer;
import kea.stopwords.StopwordsEnglish;

import org.apache.xmlrpc.WebServer;

import weka.core.Attribute;
import weka.core.FastVector;
import weka.core.Instance;
import weka.core.Instances;

public class KEAServer {

	
	private Logger myLogger = Logger.getLogger(getClass().getName());
	
	private KEAKeyphraseExtractor ke = new KEAKeyphraseExtractor();
	
	private KEAFilter m_KEAFilter = null;
	
	
	public KEAServer(String model) {
		setOptions(model);	
		try {
			loadModel(model);
			m_KEAFilter.setDebug(true);			
			myLogger.info("Loaded model " +model);
		} catch (Exception e) {			
			myLogger.log(Level.SEVERE, "Failed loading model {0} , exception: {1}", new Object[]{model, e.toString()});
		}
	}
	

	 public String[] extractKeyphrases(String document) {		 
		 
		 List<String> keyWords = new ArrayList<String>();
		 List<Instance> instances = null;

		 try {
			myLogger.info("-- Extracting Keyphrases... ");
			instances = myExtractKeyphrases(document);
		} catch (Exception e) {
			System.err.println(e.getMessage());
			e.printStackTrace();
		}
		 
		 for (Instance anInstance: instances ) {			 
			 String instanceStr = anInstance.toString();
			 //http://www.fao.org/aos/agrovoc#c_23903,'Calliandra calothyrsus',0.009212,0.000122,1,1,2,0.975066,1,True
			 //myLogger.info(instanceStr); 
			 // pick whatever data you need
			 String keyWord = instanceStr.substring(instanceStr.indexOf(",")+1, instanceStr.indexOf(",0"));			 
			 keyWords.add(keyWord);
		 } 
		
		 String[] phrases = new String[keyWords.size()];
		 keyWords.toArray(phrases);
		 myLogger.info("Keyphrases: " + Arrays.toString(phrases));
		 
		 return phrases;
	 }
	
	
	
	
	/**
	 * How to start the service 
	 * 
	 * @param args
	 */
	
	public static void main(String[] args) {
		
		int s = args.length;		
		int port = 8000;
		String model = null;
		
		if (s < 1) {			
			System.err
					.println("Usage: java kea.main.KEAServer <model> [port]\nDefault: port=8000");
			System.exit(0);
		} else {	
			model = args[0];
			if (s > 1 ) { 
				// maybe it's a number for port
				try {
					port = Integer.parseInt(args[1]);
				} catch (NumberFormatException e) {						
					System.err.println("Bad port number" +args[1] +", using default 8000");					
				}
			}			
		}
		
		String localhost = "127.0.0.1";	
		try {
			localhost = InetAddress.getLocalHost().getHostAddress();				
		} catch (UnknownHostException e1) {
					// maybe it's a number for port
			System.err.println("Bad address.\n"+e1.getMessage());									
		
		}					
				
		System.out.println("Accepting request from addesses: " + localhost);
		
		// we have everything we need, go ahead and start 			
		try {
			System.out.println("Starting server on port: " + port);
			KEAServer kea = new KEAServer(model);
			WebServer server = new WebServer(port);
			//server.setParanoid(true);
			server.acceptClient(localhost);		// add hosts here
			server.addHandler("kea", kea);
			server.start();
			System.out.println("Server started ");
		} catch (Exception e) {
			System.err.println(e.getMessage());
			e.printStackTrace();
			System.exit(0);
		}
	}
	 
 
	
	// from TestKea 
	private void setOptions(String model) {
		
		//  Name of the model -- give the path to the model 
		ke.setModelName(model);
		 
		//  Name of the vocabulary -- name of the file (without extension) that is stored in VOCABULARIES
		//    or "none" if no Vocabulary is used (free keyphrase extraction).
		//ke.setVocabulary("agrovoc");
		ke.setVocabulary("none");
		
		// Optional arguments if you want to change the defaults
		
		// Encoding of the document
		ke.setEncoding("UTF-8");
		
		// Language of the document -- use "es" for Spanish, "fr" for French
		//    or other languages as specified in your "skos" vocabulary 
		ke.setDocumentLanguage("en"); // es for Spanish, fr for French
		
		// Stemmer -- adjust if you use a different language than English or want to alterate results
		// (We have obtained better results for Spanish and French with NoStemmer)
		ke.setStemmer(new PorterStemmer());
		
		// Stopwords
		ke.setStopwords(new StopwordsEnglish());
		
		// Number of Keyphrases to extract
		ke.setNumPhrases(10);
		
		// Set to true, if you want to compute global dictionaries from the test collection
		ke.setBuildGlobal(false);		
	}
	
	 
	 private  void loadModel(String modelName) throws Exception {
			
			BufferedInputStream inStream =
				new BufferedInputStream(new FileInputStream(modelName));
			ObjectInputStream in = new ObjectInputStream(inStream);
			 m_KEAFilter = (KEAFilter)in.readObject();		
			in.close();			
		}
	  
	 private List<Instance> myExtractKeyphrases(String document)
			throws Exception {

		// Check whether there is actually any data
		//
		if (document.length() == 0 || document.equals("")) {
			throw new Exception("Couldn't find any data!");
		}

		FastVector atts = new FastVector(3);
		atts.addElement(new Attribute("doc", (FastVector) null));
		atts.addElement(new Attribute("keyphrases", (FastVector) null));
		Instances data = new Instances("keyphrase_training_data", atts, 0);

		List<Instance> myInstances = new ArrayList<Instance>();

		double[] newInst = new double[2];
		newInst[0] = (double) data.attribute(0).addStringValue(document);
		newInst[1] = Instance.missingValue();

		data.add(new Instance(1.0, newInst));

		m_KEAFilter.input(data.instance(0));

		data = data.stringFreeStructure();
		
		int numPhrases = ke.getNumPhrases();
		
		Instance[] topRankedInstances = new Instance[numPhrases];
		Instance inst;

		// Iterating over all extracted keyphrases (inst)
		while ((inst = m_KEAFilter.output()) != null) {
			int index = (int) inst.value(m_KEAFilter.getRankIndex()) - 1;

			if (index < numPhrases) {
				topRankedInstances[index] = inst;
			}
		}

		double numExtracted = 0, numCorrect = 0;

		for (int i = 0; i < numPhrases; i++) {
			if (topRankedInstances[i] != null) {
				if (!topRankedInstances[i].isMissing(topRankedInstances[i]
						.numAttributes() - 1)) {
					numExtracted += 1.0;
				}
				if ((int) topRankedInstances[i].value(topRankedInstances[i]
						.numAttributes() - 1) == 1) {
					numCorrect += 1.0;
				}
				myInstances.add(topRankedInstances[i]);				
			}
		}

		return myInstances;
	}
	
}
