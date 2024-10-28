

create_database:
	if [ -d "candidates_db" ]; then \
		rm -r candidates_db; \
	fi; \
	python preprocessing.py

launch_app:
	streamlit run main.py

run_app :
	make create_database
	make launch_app



