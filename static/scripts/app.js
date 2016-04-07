// Note: The REST API on the server only defines an error attribute if there is an error
// Thus if (response.data.error !== undefined) confirms an error occured if evaluated to true
// When perform requests using angular's $http service

var kabarakApp = angular.module("KabarakApp", []);
/**
 * COnfigur angular to prevent conflicts with jinja by changing expression symbols
 */
kabarakApp.config(['$interpolateProvider', function ($interpolateProvider) {
	$interpolateProvider.startSymbol('{[');
	$interpolateProvider.endSymbol(']}');
}]);

/**
 * Custom service to login user
 */
kabarakApp.factory("sendlogin", ["$http", "$q", function ($http, $q) {
	var util_login = {
		postData: function (data) {
			return $q(function (resolve, reject) {
				$http({
					method: "POST"
					, url: "/login_authenticate"
					, headers: {
						"Content-Type": "x-www-form-urlencoded"
					}
					, data: {
						username: data.username
						, password: data.password
					}
				}).then(function success(response) {
					console.warn(response.data)
						// The REST API on the server only defines an error attribute if there is an error
					if (response.data.error !== undefined) {
						console.error(response.data.error);
						reject(response)
					}
					resolve(response);
				}, function failure(response) {
					// Using double equals comparison because null literal will be true in this case
					if (response.data == undefined) {
						response.data = {
							error: "Connection problem, couldn't reach the server! Try again later."
						};
						reject(response);
					}
					console.error(response);
					reject(response);
				});

			});
		}


	}
	return util_login;



}]);


kabarakApp.controller("loginCTRL", ["$scope", "$window", "sendlogin", function ($scope, $window, sendlogin) {
	$scope.user = {};
	$scope.messages = {};
	$scope.messages.alert = "weeewe"
	$scope.toggleError = function () {
		$scope.messages.error = false;
	};


	$scope.loginFunction = function () {
		var promise = sendlogin.postData($scope.user);
		promise.then(function success(response) {
			console.log(response.data)
			$scope.user = response.data;
			console.log($scope.user);
			$window.location.href = "/home";
		}, function failed(response) {
			console.warn(response)
			$scope.messages = {
				alert: response.data.error
				, error: true
			}
		});
	};

}]);


kabarakApp.factory("checkDetail", ["$http", "$q", function ($http, $q) {
	return checkData = {
		check: function (detailType) {
			// detailType format { name: "email|username|nationaid", value: "value of 'name'"}
			//Depending on provided detailType  modify the data sent over $http
			posted = {};
			if (detailType.name === "username") {
				posted = {
					"username": detailType.value
				};
			} else if (detailType.name === "email") {
				posted = {
					"email": detailType.value
				};
			} else if (detailType.name === "nationalid") {
				posted = {
					"nationalid": detailType.value
				};
			}
			return $q(function (resolve, reject) {
				$http({
					method: "GET"
					, url: "/register_authenticate?" + detailType.name + "=" + detailType.value
					, headers: {
						"Content-Type": "application/json"
					}
				}).then(function success(response) {
					if (response.data.error !== undefined) {
						// There was an error, the checked detail is most probobably duplicate
						console.error(response.data.error)
						response.data.error = "The fields marked in red are invalid. Already Exist in database!"
						reject(response);
					}
					resolve(response);
				}, function failure(response) {
					if (response.data == undefined) {
						//means that data is set to null which means the connection to the server is broken
						response.data = {
							error: "Connection problem, couldn't reach the server! Try again later."
						};

						reject(response);
					}
					reject(response);
				});
			});
		}
	}
}]);

kabarakApp.factory("validate", ["checkDetail", function (checkDetail) {
	// Custom service to perform input validation
	return {
		checkUserName: function (user) {
			if (user.Username.trim() === "") {
				return;
			}
			var promise = checkDetail.check({
				name: "username"
				, value: user.Username
			});


			// reset CSS class first
			$("input[ng-model='user.Username']").removeClass("input-valid").removeClass("input-invalid");
			promise.then(function success(response) {
				user.toggleProp("UserNameValid", true);
				user.message.display = true;
				user.message.content = response.data.success;
				user.message.type = "success";
				$("input[ng-model='user.Username']").parent().removeClass("input-invalid-after");
				$("input[ng-model='user.Username']").addClass("input-valid").parent().addClass("input-valid-after");
			}, function failure(response) {
				user.toggleProp("UserNameValid", false);
				user.message.display = true;
				user.message.content = response.data.error;
				user.message.type = "alert";
				$("input[ng-model='user.Username']").parent().removeClass("input-valid-after");
				$("input[ng-model='user.Username']").addClass("input-invalid").parent().addClass("input-invalid-after");
			});

			return promise;

		}
		, checkEmail: function (user) {

			var promise = checkDetail.check({
				name: "email"
				, value: user.Email
			});
			$("input[ng-model='user.Email']").removeClass("input-valid").removeClass("input-invalid");
			promise.then(function success(response) {
				user.toggleProp("EmailValid", true);
				user.message.display = true;
				user.message.content = response.data.success;
				user.message.type = "success";
				$("input[ng-model='user.Email']").parent().removeClass("input-invalid-after");
				$("input[ng-model='user.Email']").addClass("input-valid").parent().addClass("input-valid-after");
			}, function failure(response) {
				user.toggleProp("EmailValid", false);
				user.message.display = true;
				user.message.content = response.data.error;
				user.message.type = "alert";
				$("input[ng-model='user.Email']").parent().removeClass("input-valid-after");
				$("input[ng-model='user.Email']").addClass("input-invalid").parent().addClass("input-invalid-after");
			});

			return promise;
		}
		, checkNationalID: function (user) {
			if (user.NationalID.trim() === "") {
				return;
			}
			var promise = checkDetail.check({
				name: "nationalid"
				, value: user.NationalID
			});
			$("input[ng-model='user.NationalID']").removeClass("input-valid").removeClass("input-invalid");
			promise.then(function success(response) {
				user.toggleProp("NationalIDValid", true);
				user.message.display = true;
				user.message.content = response.data.success;
				user.message.type = "success";
				$("input[ng-model='user.NationalID']").parent().removeClass("input-invalid-after");
				$("input[ng-model='user.NationalID']").addClass("input-valid").parent().addClass("input-valid-after");
			}, function failure(response) {
				user.toggleProp("NationalIDValid", false);
				user.message.display = true;
				user.message.content = response.data.error;
				user.message.type = "alert";
				$("input[ng-model='user.NationalID']").parent().removeClass("input-valid-after");
				$("input[ng-model='user.NationalID']").addClass("input-invalid").parent().addClass("input-invalid-after");
			});
			return promise;
		}
	};
}]);

kabarakApp.factory("register", ["$http", "$q", function ($http, $q) {
	return {
		promise: function (data) {
			return $q(function (resolve, reject) {
				$http({
					method: "POST"
					, url: "/register_authenticate"
					, data: data
					, headers: {
						"Content-Type": "x-www-form-urlencoded"
					}
				}).then(function success(response) {
					if (response.data.success !== undefined) {
						resolve(response);
					}
					reject(response);
				}, function failure(response) {
					console.warn(response.data);
					reject(response.data)
				});

			});
		}
	}
}]);


kabarakApp.controller("registerCTRL", ["$scope", "$window", "validate", "register", function ($scope, $window, validate, register) {
	$scope.user = {
		Username: ""
		, UserNameValid: null
		, Email: ""
		, EmailValid: null
		, Telephone: ""
		, TelephoneValid: null
		, NationalID: ""
		, NationalIDValid: null
		, message: {
			display: false
			, content: ""
			, type: "secondary"
		}
		, toggleProp: function (prop, val) {
			//Will toggle the value of a property from true to false and vice versa
			this["" + prop + ""] = val;
		}
		, resetUser: function () {
			this.Username = "";
			this.UserNameValid = null;
			this.Email = "";
			this.EmailValid = null;
			this.Telephone = "";
			this.TelephoneValid = null;
			this.NationalID = "";
			this.NationalIDValid = null;
			this.message = {
				display: false
				, content: ""
				, type: "secondary"
			}
		}
	};
	// hide alerts
	$scope.toggleError = function () {
		$scope.user.message.display = false;
	};
	$scope.registerFunction = function () {
		//this is run on form submit which is only done after filling valid data
		// Create object with filled data from $scope.user : These should be all antries with type string
		var data_obj = {};
		for (entry in $scope.user) {
			if (typeof $scope.user[entry] === "string") {
				data_obj[entry] = $scope.user[entry];
			}
		}

		var promise = register.promise(data_obj);
		promise.then(function success(response) {
			if (response.data.clear_data === true && response.data.success) {
				//reset the $scope.user content
				$scope.user.resetUser();
				$scope.user.message = {
					display: true
					, content: response.data.success + " Your ID: " + response.data.insert_id
					, type: "secondary"
				}
				setTimeout(function () {
					$scope.user.message = {
						display: true
						, content: "You will receive an Email once your account is approved!"
						, type: "success"
					}
				}, 2000);
				setTimeout(function () {
					$window.location.href = "/login"
				}, 2000);
			}

		}, function failure(response) {
			console.log("naaay");
			$scope.user.resetUser();
			$scope.user.message = {
				display: true
				, content: "There was an error creating your account. Please try again later!"
				, type: "alert"
			}
		});

	};

	//Will make use of the debounce configuration on the user.NationalID model to call its validate function since it is last and the user will not neccessarily blur it
	//This is important so that we can activate the register button
	//we make use of the $watch function of our scope
	$scope.$watch("user.Username", function (newValue, oldValue) {
		if ($scope.user.Username.trim().length > 0 && $scope.user.Username.trim() !== "") {
			var promise = validate.checkUserName($scope.user);
			promise.then(function success(response) {
				console.error($scope.user);
			}, function failure(response) {
				console.log("failed ...");
				console.error($scope.user);
			});

		}
	});
	$scope.$watch("user.Email", function (newValue, oldValue) {
		if ($scope.user.Email !== undefined && $scope.user.Email.trim() !== "") {
			var promise = validate.checkEmail($scope.user);;
			promise.then(function success(response) {
				console.error($scope.user);
			}, function failure(response) {
				console.log("failed ...");
				console.error($scope.user);
			});
		} else {
			$("input[ng-model='user.Email']").on("change", function () {
				if ($scope.user.Email === undefined || $scope.user.Email.trim() === "") {
					$scope.user.toggleProp("EmailValid", false);
					$("input[ng-model='user.Email']").parent().removeClass("input-valid-after");
					$("input[ng-model='user.Email']").addClass("input-invalid").parent().addClass("input-invalid-after");
				}

			})
		}
	});
	$scope.$watch("user.NationalID", function (newValue, oldValue) {
		if ($scope.user.NationalID.trim().length > 0 && $scope.user.NationalID.trim() !== "") {
			var promise = validate.checkNationalID($scope.user);
			promise.then(function success(response) {
				console.error($scope.user);
			}, function failure(response) {
				console.log("failed ...");
				console.error($scope.user);
			});
		}
	});

	$scope.$watchCollection("user", function () {
		if (($scope.user.UserNameValid === true && $scope.user.Username.trim() !== "") && ($scope.user.EmailValid === true && $scope.user.Email !== "") && ($scope.user.NationalIDValid === true && $scope.user.NationalID.trim() !== "")) {

			console.log("changed");
			$(".form.register input[type='submit']").removeAttr("disabled");
		} else {
			$(".form.register input[type='submit']").attr("disabled", "disabled");
		}
		// add
	});




}]);

kabarakApp.factory("userData", ["$http", "$q", function ($http, $q) {
	return {
		getLoggedInDetails: $q(function (resolve, reject) {
			// Fetches the user's details after a page has loaded
			$http({
				method: "GET"
				, url: "/get_user_data"
				, headers: {
					"Content-Type": "application/json"
				}
			}).then(function success(response) {
				resolve(response);
			}, function failure(response) {
				console.log(response.data);
				reject(response);
			});
		})
		, getVerifiedUsernames: $q(function (resolve, reject) {
			// Fetches last 10 registered users
			$http({
				method: "GET"
				, url: "/get_last_verified_usernames"
				, headers: {
					"Content-Type": "application/json"
				}

			}).then(function success(response) {
				resolve(response);
			}, function failure(response) {
				reject(response)
			});
		})
		, getPendingUsernames: $q(function (resolve, reject) {
			// Fetches last 10 registered users
			$http({
				method: "GET"
				, url: "/get_last_registered_usernames"
				, headers: {
					"Content-Type": "application/json"
				}

			}).then(function success(response) {
				resolve(response);
			}, function failure(response) {
				reject(response)
			});
		})
		, getHomeAdminData: $q(function (resolve, reject) {
			// Fetches last 10 registered users
			$http({
				method: "GET"
				, url: "/home_admin_data"
				, headers: {
					"Content-Type": "application/json"
				}

			}).then(function success(response) {
				resolve(response);
			}, function failure(response) {
				reject(response)
			});
		})
		, getUsersData: function (data) {
			// Currently don't have time to enforce the filters will implement later for now just fetch all users
			return $q(function (resolve, reject) {
				// Fetches last 10 registered users
				$http({
					method: "GET"
					, url: "/get_users_data/all"
					, headers: {
						"Content-Type": "application/json"
					}

				}).then(function success(response) {
					resolve(response);
				}, function failure(response) {
					reject(response)
				});
			})
		}
		, approveUser: function (data) {
			// Approves user registration request
			return $q(function (resolve, reject) {
				// Fetches last 10 registered users
				$http({
					method: "GET"
					, url: "/approve_user/" + data
					, headers: {
						"Content-Type": "application/json"
					}

				}).then(function success(response) {
					resolve(response);
				}, function failure(response) {
					reject(response)
				});
			})
		}
		, getDiscussions: function (discussion_id) {
			return $q(function (resolve, reject) {
				// Fetches discussions from server
				$http({
					method: "GET"
					, url: "/get_discussions/" + discussion_id
					, headers: {
						"Content-Type": "application/json"
					}

				}).then(function success(response) {
					resolve(response);
				}, function failure(response) {
					reject(response)
				});
			})
		}
		, getEvents: function (event_id) {
			return $q(function (resolve, reject) {
				// Fetches discussions from server
				$http({
					method: "GET"
					, url: "/get_events/" + event_id
					, headers: {
						"Content-Type": "application/json"
					}

				}).then(function success(response) {
					resolve(response);
				}, function failure(response) {
					reject(response)
				});
			})
		}
		, rejectUser: function (data) {
			// Rejects a users registration request
			return $q(function (resolve, reject) {
				// Fetches last 10 registered users
				$http({
					method: "GET"
					, url: "/reject_user/" + data
					, headers: {
						"Content-Type": "application/json"
					}

				}).then(function success(response) {
					resolve(response);
				}, function failure(response) {
					reject(response)
				});
			})
		}

	};


}]);

kabarakApp.filter("limitText", function () {
	//Limits the text to be shown for large text
	return function (text) {
		return text.substr(0, 60) + " ...";
	}
});
kabarakApp.filter("limitTextLong", function () {
	//Limits the text to be shown for large text
	return function (text) {
		return text.substr(0, 120) + " ...";
	}
});




kabarakApp.controller("adminHomeCTRL", ["$scope", "userData", function ($scope, userData) {
	$scope.user = {
		Username: ""
		, message: {
			display: false
			, type: "alert"
			, content: "An unspecified error occured"
		}
	};
	$scope.toggleAlert = function () {
		if ($scope.user.message.display) {
			$scope.user.message.display = !$scope.user.message.display;
			$scope.user.message.content = "An unspecified error occured"
		}
	};
	$scope.users = {
		verified: {}
		, pending: {}
		, discussions: []
		, events: []
	};
	// Will be used to filter displayed discussions per category
	$scope.discussions = {
		announcements: "announcements"
		, general: "general"
		, events: "events"
		, jobs: "jobs"
	};
	$scope.discussions["announcements"] = "announcements";

	userData.getLoggedInDetails.then(function success(response) {
		//Populates the details of the currently logged user
		for (detail in response.data) {
			$scope.user[detail] = response.data[detail];
		}
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});

	userData.getVerifiedUsernames.then(function success(response) {
		//Populates the details of the currently logged user
		for (user in response.data) {
			$scope.users.verified[user] = response.data[user];
		}
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});

	userData.getPendingUsernames.then(function success(response) {
		//Populates the details of the currently logged user
		for (user in response.data) {
			$scope.users.pending[user] = response.data[user];
		}
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});

	userData.getHomeAdminData.then(function success(response) {
		//Populates the recent discussions
		var i = 0
			, j = 0;
		for (discussion in response.data) {
			if (typeof response.data[discussion][1] === "number" && typeof response.data[discussion][2] === "number") {
				//Conforms to Events structure - add to events
				$scope.users.events[i] = response.data[discussion];
				i++;
			} else {
				$scope.users.discussions[j] = response.data[discussion];
				j++;
			}
		}
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});



}]);


kabarakApp.controller("adminUsersCTRL", ["$scope", "$window", "userData", function ($scope, $window, userData) {
	$scope.user = {
		Username: ""
		, message: {
			display: false
			, type: "alert"
			, content: "An unspecified error occured"
		}
	};
	$scope.users = {
		all: []
	};
	$scope.toggleAlert = function () {
		if ($scope.user.message.display) {
			$scope.user.message.display = !$scope.user.message.display;
			$scope.user.message.content = "An unspecified error occured"
		}
	};
	$scope.users.approve_user = function (user_id) {
		userData.approveUser(user_id).then(function success(response) {
			$scope.user.message = {
					display: true
					, type: "success"
					, content: "User ID: " + user_id + "  VERIFIED successfully!"
				}
				// Update UI
			$('tbody span#status-' + user_id).removeClass("secondary").addClass("success");
		}, function failure(response) {
			$scope.user.message = {
				display: true
				, type: "alert"
				, content: "Failed! User ID: " + user_id + "  wasn't approved!"
			}
		});
	};

	$scope.users.reject_user = function (user_id) {
		userData.rejectUser(user_id).then(function success(response) {
			$scope.user.message = {
					display: true
					, type: "warning"
					, content: "User ID: " + user_id + "  has been denied access!"
				}
				// Update UI
			$('tbody span#status-' + user_id).removeClass("success").addClass("secondary");
		}, function failure(response) {
			$scope.user.message = {
				display: true
				, type: "alert"
				, content: "Failed! Access of User ID: " + user_id + " couldn't be revoked!"
			}
		});
	};


	userData.getLoggedInDetails.then(function success(response) {
		//Populates the details of the currently logged user
		for (detail in response.data) {
			$scope.user[detail] = response.data[detail];
		}
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});

	filter = $window.location.pathname.split("/")[1]
	userData.getUsersData("pending").then(function success(response) {
		// Currently don't have time to enforce the filters will implement later for now just fetch all users
		for (user in response.data) {
			$scope.users.all[user] = response.data[user];
		}
		$scope.users.all.forEach(function (user) {
			// Truncate registration status
			user[10] = user[10].substr(0, 3).toUpperCase();
			// is Verified?
			if (user[10] === "VER") {
				user.push(false);
			} else {
				user.push(true);
			}

		});
		//Style the registration status badges
		setTimeout(function () {
			$("tbody td .badge:contains('VER')").addClass("success");
			$("tbody td .badge:contains('PEN')").addClass("warning");
		}, 500);
		console.log($scope.users)
	}, function failure(response) {
		console.error("Error! Couldn't fetch users.");
		$scope.user.message = {
			display: true
			, type: "alert"
			, content: "Error! Couldn't fetch users. Please try again later!"
		};
	});




}]);


kabarakApp.controller("dicussionsCTRL", ["$scope", "$window", "userData", function ($scope, $window, userData) {
	$scope.user = {
		Username: ""
		, message: {
			display: false
			, type: "alert"
			, content: "An unspecified error occured"
		}
	};
	$scope.discussions = [];
	$scope.toggleAlert = function () {
		if ($scope.user.message.display) {
			$scope.user.message.display = !$scope.user.message.display;
			$scope.user.message.content = "An unspecified error occured"
		}
	};
	userData.getLoggedInDetails.then(function success(response) {
		//Populates the details of the currently logged user
		for (detail in response.data) {
			$scope.user[detail] = response.data[detail];
		}
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});
	if ($window.location.pathname === "/discussions") {
		userData.getDiscussions("all").then(function success(response) {
			for (discussion in response.data) {
				$scope.discussions[discussion] = response.data[discussion];
			}
			console.warn($scope.discussions);
		}, function failure(response) {
			//Show error message
			$scope.toggleAlert();

		});
	}





}]);



kabarakApp.controller("eventsCTRL", ["$scope", "$window", "userData", function ($scope, $window, userData) {
	$scope.user = {
		Username: ""
		, message: {
			display: false
			, type: "alert"
			, content: "An unspecified error occured"
		}
	};
	$scope.events = [];
	$scope.toggleAlert = function () {
		if ($scope.user.message.display) {
			$scope.user.message.display = !$scope.user.message.display;
			$scope.user.message.content = "An unspecified error occured"
		}
	};
	userData.getLoggedInDetails.then(function success(response) {
		//Populates the details of the currently logged user
		for (detail in response.data) {
			$scope.user[detail] = response.data[detail];
		}
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});

	if ($window.location.pathname === "/events") {
		//fetch all events
		userData.getEvents("all").then(function success(response) {
			for (event in response.data) {
				$scope.events[event] = response.data[event];
			}
			console.warn($scope.events);
		}, function failure(response) {
			//Show error message
			$scope.toggleAlert();

		});
	}


}]);

kabarakApp.controller("singleDiscussionCTRL", ["$scope", "$window", "userData", function ($scope, $window, userData) {
	$scope.user = {
		Username: ""
		, message: {
			display: false
			, type: "alert"
			, content: "An unspecified error occured"
		}
	};
	$scope.discussion = [];
	$scope.toggleAlert = function () {
		if ($scope.user.message.display) {
			$scope.user.message.display = !$scope.user.message.display;
			$scope.user.message.content = "An unspecified error occured"
		}
	};
	userData.getLoggedInDetails.then(function success(response) {
		//Populates the details of the currently logged user
		for (detail in response.data) {
			$scope.user[detail] = response.data[detail];
		}
		console.warn($scope.user)
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});
	
	var locationData = $window.location.pathname.split("/")[2];
	if (Number.parseInt(locationData) !== NaN) {
		// It's a number !
		userData.getDiscussions(locationData).then(function success(response) {
			for (detail in response.data) {
				$scope.discussion[detail] = response.data[detail];
			}
			console.warn($scope.discussion);
		}, function failure(response) {
			//Show error message
			$scope.toggleAlert();

		});
	}
	
}]);



kabarakApp.controller("singleEventCTRL", ["$scope", "$window", "userData", function ($scope, $window, userData) {
	$scope.user = {
		Username: ""
		, message: {
			display: false
			, type: "alert"
			, content: "An unspecified error occured"
		}
	};
	$scope.event = [];
	$scope.toggleAlert = function () {
		if ($scope.user.message.display) {
			$scope.user.message.display = !$scope.user.message.display;
			$scope.user.message.content = "An unspecified error occured"
		}
	};
	userData.getLoggedInDetails.then(function success(response) {
		//Populates the details of the currently logged user
		for (detail in response.data) {
			$scope.user[detail] = response.data[detail];
		}
		console.warn($scope.user)
	}, function failure(response) {
		//Show error message
		$scope.toggleAlert();

	});
	
	
	var locationData = $window.location.pathname.split("/")[2];
	if (Number.parseInt(locationData) !== NaN) {
		// It's a number !
		userData.getEvents(locationData).then(function success(response) {
			for (detail in response.data) {
				$scope.event[detail] = response.data[detail];
			}
			console.warn($scope.event);
		}, function failure(response) {
			//Show error message
			$scope.toggleAlert();

		});
	}
}]);