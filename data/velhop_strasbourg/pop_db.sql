INSERT INTO veloscope."user" (username,password_hashed,email,"role",is_active) VALUES
	 ('admin','6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b','admin@gmail.com','ADMIN',true), -- password: 1
	 ('user0','6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b','user0@gmail.com','USER',true); -- password: 1

INSERT INTO veloscope.system_information (system_id,"language","name",url,start_date,phone_number,email,timezone) VALUES
	 ('nextbike_ae','fr','Vélhop - Strasbourg','https://vls.velhop.strasbourg.eu/',NULL,'+33 367 70 70 70','contact@velhop.strasbourg.eu','Europe/Berlin');

INSERT INTO veloscope.station_information (station_id,"name",short_name,lat,lon,address,is_virtual_station,station_area,contact_phone,capacity,is_charging_station) VALUES
	 ('245557155','Bischheim Gare','62000',48.611639,7.742056,NULL,false,NULL,NULL,5,NULL),
	 ('245557947','Bischheim Espace Européen','62001',48.616361,7.720056,NULL,false,NULL,NULL,10,NULL),
	 ('245559919','Entzheim Gare','62003',48.547222,7.628056,NULL,false,NULL,NULL,10,NULL),
	 ('245564614','Geispolsheim Gare','62004',48.521222,7.684944,NULL,false,NULL,NULL,5,NULL),
	 ('638093766','Graffenstaden Gare','62043',48.532635,7.690003,NULL,false,NULL,NULL,10,NULL),
	 ('245566026','Hoenheim Gare','62005',48.628333,7.758833,NULL,false,NULL,NULL,10,NULL),
	 ('245576518','Campus d''Illkirch','62007',48.528917,7.732778,NULL,false,NULL,NULL,10,NULL),
	 ('500084605','Salle des fêtes','62006',48.524194,7.707583,NULL,false,NULL,NULL,10,NULL),
	 ('245580402','La Wantzenau Gare','62008',48.664972,7.824972,NULL,false,NULL,NULL,8,NULL),
	 ('245581065','Lingolsheim Gare','62009',48.559694,7.678194,NULL,false,NULL,NULL,6,NULL),
	 ('245581709','Mundolsheim Gare','62010',48.645404,7.721483,NULL,false,NULL,NULL,9,NULL),
	 ('245582029','Oberhausbergen Mairie','62011',48.605593,7.685699,NULL,false,NULL,NULL,6,NULL),
	 ('245582844','Schiltigheim Mairie','62012',48.606417,7.749778,NULL,false,NULL,NULL,20,NULL),
	 ('245584292','Strasbourg Gare Centrale','62013',48.584306,7.73475,NULL,false,NULL,NULL,50,NULL),
	 ('245585106','Roethig Gare','62014',48.563583,7.694944,NULL,false,NULL,NULL,10,NULL),
	 ('245585847','Elsau','62015',48.56775,7.726917,NULL,false,NULL,NULL,10,NULL),
	 ('245586606','Rotonde','62016',48.591806,7.725278,NULL,false,NULL,NULL,15,NULL),
	 ('245587953','Rives de l Aar','62017',48.599972,7.754306,NULL,false,NULL,NULL,10,NULL),
	 ('245588745','Robertsau Boecklin','62018',48.598108,7.778822,NULL,false,NULL,NULL,16,NULL),
	 ('245589413','Poteries','62019',48.583333,7.691639,NULL,false,NULL,NULL,10,NULL),
	 ('245590268','Citadelle','62037',48.5709,7.779822,NULL,false,NULL,NULL,10,NULL),
	 ('245591123','Halles','62021',48.588024,7.740345,NULL,false,NULL,NULL,15,NULL),
	 ('245591375','République','62022',48.587757,7.755487,NULL,false,NULL,NULL,10,NULL),
	 ('245591893','Austerlitz','62023',48.578111,7.751944,NULL,false,NULL,NULL,32,NULL),
	 ('245592472','Parc des Romains','62024',48.581129,7.723453,NULL,false,NULL,NULL,12,NULL),
	 ('245593080','Broglie','62025',48.585333,7.749722,NULL,false,NULL,NULL,28,NULL),
	 ('245594460','Université','62026',48.582028,7.766611,NULL,false,NULL,NULL,20,NULL),
	 ('245595123','Place Arnold','62027',48.584528,7.768694,NULL,false,NULL,NULL,15,NULL),
	 ('245599491','Parlement','62033',48.5995,7.766917,NULL,false,NULL,NULL,10,NULL),
	 ('245602743','Musée d''Art Moderne','62034',48.580306,7.736,NULL,false,NULL,NULL,16,NULL),
	 ('245603512','Place de Bordeaux','62035',48.593778,7.757361,NULL,false,NULL,NULL,8,NULL),
	 ('499948064','Rotterdam','62020',48.581564,7.782014,NULL,false,NULL,NULL,10,NULL),
	 ('499949546','Jean Jaurès','62002',48.567206,7.772907,NULL,false,NULL,NULL,7,NULL),
	 ('245604683','Vendenheim Gare','62036',48.665556,7.718611,NULL,false,NULL,NULL,10,NULL),
	 ('586719545','Wolfisheim','62039',48.591485,7.672662,NULL,false,NULL,NULL,10,NULL),
	 ('245595689','Place du Marché','62028',48.566222,7.759222,NULL,false,NULL,NULL,15,NULL),
	 ('245596275','Place d''Islande','62029',48.580417,7.776972,NULL,false,NULL,NULL,12,NULL),
	 ('245597085','Etoile Bourse','62030',48.574417,7.753833,NULL,false,NULL,NULL,20,NULL),
	 ('245597920','Etoile Cinéma','62031',48.573512,7.762392,NULL,false,NULL,NULL,16,NULL),
	 ('245598687','Krimmeri Gare','62032',48.561806,7.751889,NULL,false,NULL,NULL,10,NULL);

