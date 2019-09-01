odoo.define('popup_notifications.popup_notifications', function (require) {
  "use strict";
    var WebClient = require('web.WebClient');
    var core = require('web.core');
    var QWeb = core.qweb;
    var session = require('web.session');
   
    WebClient.include({
        check_popup_notifications: function () {
            console.log('Called')
            var self = this;
            session.rpc('/popup_notifications/notify',
			 {}, {shadow: true})
                .done(
                    function (notifications) {
                        _.each(notifications, function (notif) {
                            if (notif.status == 'draft'){
                            setTimeout(function () {
                                if ($('.ui-notify-message p#p_id').filter(function () {
                                    return $(this).html() == notif.id;
                                }).length) {
                                    return;
                                } // prevent displaying same notifications
                                notif.title = QWeb.render('popup_title', {'title': notif.title, 'id': notif.id});
                                notif.message += QWeb.render('popup_footer');
                                self.do_notify(notif.title, notif.message, true);
				/**self.$el.find(".link2detail").on('click', function () {
				 console.log(">>>>>>>>>>>>>",notif.sale_id)
                                    session.rpc("/popup_notifications/sale", {'sale_id': notif.sale_id});
                                   
                                }); **/
				self.$el.find(".link2detail").on('click', function () {
                                   /**self._rpc({
				        route: '/web/action/load',
				        params: {
				            action_id: 'sale.action_quotations_salesteams',
				        },
					    		})
					    .then(function(r) {
						console.log(">>>>>>>>>>>>>>>", self.eid ,r)
						r.res_id = notif.sale_id;
					        r.active_id =  notif.sale_id;
						return self.do_action(r);
					    });**/
                                                  self.do_action({
						    type: 'ir.actions.act_window',
						    res_model:'sale.order',
						    view_type: 'form',
                                                    view_mode: 'form',
						    views: [[false, 'form']],
						    res_id: notif.sale_id,
						   target: 'curret',
						});
					self.$el.find('.o_notification_manager').hide();
					session.rpc("/popup_notifications/notify_ack", {'notif_id': notif.id});
                                   
                                });

				

                                self.$el.find(".link2showed").on('click', function () {
                                    console.log(self.$el)
                                    self.$el.find('.o_notification_manager').hide();
                                    session.rpc("/popup_notifications/notify_ack", {'notif_id': notif.id});
                                });
                            }, 1000);
			}
                        });
                    }
                )
                .fail(function (err, ev) {
                    if (err.code === -32098) {
                        // Prevent the CrashManager to display an error
                        // in case of an xhr error not due to a server error
                        ev.preventDefault();
                    }
                });
        },

        start: function () {
            var self = this;
            self._super();
            $(document).ready(function () {
                self.check_popup_notifications();
                 setInterval(function () {
                    self.check_popup_notifications();
                },5 * 1000);
            });
	
	    
	    
        },

    })
});
