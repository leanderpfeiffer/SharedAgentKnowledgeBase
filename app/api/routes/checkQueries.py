checkRightOrder = """prefix : 		<http://PAonto.com#> 
        prefix owl: 	<http://www.w3.org/2002/07/owl#> 
        prefix rdf: 	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> 
        prefix rdfs: 	<http://www.w3.org/2000/01/rdf-schema#> 
        prefix xsd: 	<http://www.w3.org/2001/XMLSchema#> 

        # Feature 1 is completed after feature 2, while the specification defines the oposite
        SELECT ?spec ?feature1 ?endTime1 ?feature2 ?endTime2 WHERE {
            ?spec a/rdfs:subClassOf* :specification {
                ?spec :hadProductionStep ?ps1.
                ?spec :hadProductionStep ?ps2.
                ?ps1 :implementedFeature ?feature1;   
                    :endTime ?endTime1.
                ?ps2 :implementedFeature ?feature2;
                     :endTime ?endTime2.
                ?feature1 a ?feat1class.
                ?feature2 a ?feat2class.
                ?feat1class rdfs:subClassOf [
#			        rdf:type owl:Restriction ; 
			        owl:onProperty :fprecedes ; 
			        owl:someValuesFrom ?feat2class ] . 
                FILTER(?endTime1 > ?endTime2)
            }               
        }ORDER BY ?endTime"""

checkStart = """prefix : 		<http://PAonto.com#> 
prefix owl: 	<http://www.w3.org/2002/07/owl#> 
prefix rdf: 	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> 
prefix rdfs: 	<http://www.w3.org/2000/01/rdf-schema#> 
        prefix xsd: 	<http://www.w3.org/2001/XMLSchema#> 

        # Returns true if first feature, which is implemented is start
        ASK{
            ?spec a/rdfs:subClassOf* :specification; 
                :hadProductionStep ?ps1.
                ?ps1 :implementedFeature ?feature;   
                    :endTime ?endTime.
                ?feature a/rdfs:subClassOf* :none
            }ORDER BY ?endTime LIMIT 1"""