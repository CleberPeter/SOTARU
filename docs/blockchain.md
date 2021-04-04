# Blockchain

This section describes the types and structure of each of the blockchain blocks.

### Add Node
	header
		size:                1024
		type:                "add_node"
		name:                "A"
		hash_previous_block: "f4f14079719f404b8556018069d3c81eebfee64f00c59b85813101eacc367a96"
	body
		host:      "localhost"
		tcp_port:  5057
		http_port: 8080
		
### Add Author
	header
		size:                1024
		type:                "add_author"
		name:                "G3PD"
		hash_previous_block: "f4f14079719f404b8556018069d3c81eebfee64f00c59b85813101eacc367a96"
	body
		email:      "admin@g3pd.com.br"
		password:   "db3fef373cb224f4f66da38e4001401af969c629171f4f7fbdeb457fe4a94001"
		public_key: "0421a15f19bf6e3b1ca0f25f840460e4d9067aa4e158cbe1af6ef9db8257209f51978bfbc018f862150ff6b2890fb67a415b380092c90d6b4850cdff1df1d57d0b"
